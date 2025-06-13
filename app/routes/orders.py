from flask import Blueprint, request, jsonify
from psycopg2 import sql
from app.db import get_connection

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/add_order', methods=['POST'])
def add_order():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM orders WHERE tgid = %s AND status = '' AND archive = 0", (data['tgid'],))
        if cursor.fetchone():
            return jsonify({'message': 'Pending order already exists'}), 409
        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM orders")
        new_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO orders (id, tgid, username, ordertext, status, count, price, location, archive)
            VALUES (%s, %s, %s, %s, '', -1, -1, '', 0)
        """, (new_id, data['tgid'], data['username'], data['ordertext']))
        conn.commit()
        return jsonify({'message': 'Order added', 'id': new_id}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@orders_bp.route('/get_all_orders', methods=['GET'])
def get_all_orders():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE archive = 0 ORDER BY id ASC")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    orders = [dict(zip(columns, row)) for row in rows]
    cursor.close()
    conn.close()
    return jsonify({'status': 'success', 'orders': orders, 'count': len(orders)}), 200


@orders_bp.route('/update_order/<int:order_id>', methods=['PATCH'])
def update_order(order_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    allowed_fields = ['tgid', 'username', 'ordertext', 'status', 'count', 'price', 'location', 'archive']
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


@orders_bp.route('/filter', methods=['GET'])
def filter_orders():
    filters = request.args.to_dict()
    query = "SELECT * FROM orders"
    values = []

    conditions = []
    for key, value in filters.items():
        conditions.append(f"{key} = %s")
        values.append(value)

    if 'archive' not in filters:
        conditions.append("archive = 0")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        orders = [dict(zip(columns, row)) for row in rows]
        return jsonify({'status': 'success', 'orders': orders, 'count': len(orders)}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()