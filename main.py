from flask import Flask, request, jsonify
from flask_cors import CORS

import psycopg2
from psycopg2 import sql
import logging

app = Flask(__name__)
CORS(app)

# Настройки подключения к PostgreSQL
DB_CONFIG = {
    "user": "poizonapi",
    "password": "91546",
    "host": "localhost",
    "port": "5432",
    "database": "poizon"
}

# Установим логгирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_orders_table():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                tgid INTEGER NOT NULL,
                username TEXT NOT NULL,
                ordertext TEXT NOT NULL,
                status TEXT NOT NULL,
                count INTEGER,
                price INTEGER,
                location TEXT
            );
        """)
        conn.commit()
    except Exception as e:
        logger.error(f"Ошибка при создании таблицы: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()


def init_db():
    create_orders_table()

@app.route('/add_order', methods=['POST'])
def add_order():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM orders WHERE tgid = %s AND status = ''", (data['tgid'],))
        if cursor.fetchone():
            return jsonify({'message': 'Pending order already exists'}), 400

        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM orders")
        new_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO orders (id, tgid, username, ordertext, status, count, price, location)
            VALUES (%s, %s, %s, %s, '', -1, -1, '')
        """, (new_id, data['tgid'], data['username'], data['ordertext']))

        conn.commit()
        return jsonify({'message': 'Order added', 'id': new_id}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/get_order_tgId/<int:tgid>', methods=['GET'])
def get_order_by_tgid(tgid):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE tgid = %s", (tgid,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return jsonify({'status': 'success', 'order': dict(zip(columns, row))}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/get_order_id/<int:order_id>', methods=['GET'])
def get_order_by_id(order_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return jsonify({'status': 'success', 'order': dict(zip(columns, row))}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/get_all_orders', methods=['GET'])
def get_all_orders():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders ORDER BY id ASC")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        orders = [dict(zip(columns, row)) for row in rows]
        return jsonify({'status': 'success', 'orders': orders, 'count': len(orders)}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/delete_order_id/<int:order_id>', methods=['DELETE'])
def delete_order_by_id(order_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
        if cursor.rowcount == 0:
            return jsonify({'error': 'Order not found'}), 404
        conn.commit()
        return jsonify({'message': 'Order deleted'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/delete_order_tgid/<int:tgid>', methods=['DELETE'])
def delete_order_by_tgid(tgid):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE tgid = %s", (tgid,))
        if cursor.rowcount == 0:
            return jsonify({'error': 'No orders found'}), 404
        conn.commit()
        return jsonify({'message': 'Orders deleted'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/update_order/<int:order_id>', methods=['PATCH'])
def update_order(order_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    allowed_fields = ['tgid', 'username', 'ordertext', 'status', 'count', 'price', 'location']
    update_fields = []
    update_values = []

    for field in allowed_fields:
        if field in data:
            update_fields.append(sql.Identifier(field))
            update_values.append(data[field])

    if not update_fields:
        return jsonify({'error': 'No valid fields to update'}), 400

    update_values.append(order_id)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = sql.SQL("UPDATE orders SET {} WHERE id = %s").format(
            sql.SQL(', ').join(
                sql.SQL("{} = %s").format(field) for field in update_fields
            )
        )
        cursor.execute(query, update_values)
        conn.commit()
        return jsonify({'message': 'Order updated'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/clear_orders', methods=['DELETE'])
def clear_orders():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders")
        conn.commit()
        return jsonify({'message': 'All orders cleared'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/filter', methods=['GET'])
def filter_orders():
    filters = request.args.to_dict()
    query = "SELECT * FROM orders"
    values = []

    if filters:
        conditions = []
        for key, value in filters.items():
            conditions.append(f"{key} = %s")
            values.append(value)
        query += " WHERE " + " AND ".join(conditions)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        orders = [dict(zip(columns, row)) for row in rows]
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


init_db()


if __name__ == '__main__':
    app.run(debug=True)
