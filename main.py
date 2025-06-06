from flask import Flask, request, jsonify
from flask_cors import CORS

import json
import psycopg2
from psycopg2 import sql
app = Flask(__name__)
CORS(app)
ORDERS_FILE = 'orders.json'

# Настройки подключения к PostgreSQL (замените на свои)
DB_CONFIG = {
    "user": "poizonApi",
    "password": "401_SSD52",
    "host": "localhost",
    "port": "5432",
    "database": "poizon"
}

def get_connection():
    """Устанавливает соединение с PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


def create_orders_table():
    """Создаёт таблицу orders, если её нет."""
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
        print(f"Ошибка при создании таблицы: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()


def save_orders(orders):
    """Сохраняет список заказов в базу данных."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Создаём таблицу (если её нет)
        create_orders_table()

        # Вставляем или обновляем заказы
        for order in orders:
            cursor.execute("""
                INSERT INTO orders (id, tgid, username, ordertext, status, count, price, location)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET 
                    tgid = EXCLUDED.tgid,
                    username = EXCLUDED.username,
                    ordertext = EXCLUDED.ordertext,
                    status = EXCLUDED.status,
                    count = EXCLUDED.count,
                    price = EXCLUDED.price,
                    location = EXCLUDED.location;
            """, (
                order["id"],
                order["tgid"],
                order["username"],
                order["ordertext"],
                order["status"],
                order["count"],
                order["price"],
                order["location"]
            ))

        conn.commit()
        print(f"Успешно сохранено {len(orders)} заказов.")

    except Exception as e:
        print(f"Ошибка при сохранении заказов: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()


def load_orders():
    """Загружает все заказы из базы данных."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM orders;")
        columns = [desc[0] for desc in cursor.description]
        orders = []

        for row in cursor.fetchall():
            order = dict(zip(columns, row))
            orders.append(order)

        return orders

    except Exception as e:
        print(f"Ошибка при загрузке заказов: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()



def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# def load_orders():
#     if os.path.exists(ORDERS_FILE):
#         with open(ORDERS_FILE, 'r') as f:
#             return json.load(f)
#     return []
#
#
# def save_orders(orders):
#     with open(ORDERS_FILE, 'w') as f:
#         json.dump(orders, f, indent=4)



def generate_id(orders):
    if not orders:
        return 1
    return max(order['id'] for order in orders) + 1

def key_in_dictionary(dic, key):
    if key in list(dic.keys()):
        return True
    else:
        return False


@app.route('/add_order', methods=['POST'])
def add_orders():
    """Добавление товара"""
    user_data = request.get_json()
    if not user_data:
        return jsonify({'error': 'No JSON data provided'}), 400
    orders = load_orders()

    for order in orders:
        if order["tgid"] == user_data['tgid'] and order["status"] == "":
            return jsonify({
                "status": "success",
                "message": f"This user order is in pending status"
            }), 404
    new_id = generate_id(orders)
    user_data['id'] = new_id
    user_data['status'] = ""
    user_data['count'] = -1
    user_data['price'] = -1
    user_data['location'] = ''
    orders.append(user_data)
    save_orders(orders)
    return jsonify({'message': 'User added successfully', 'id': new_id}), 200




@app.route('/get_order_tgId/<int:order_id>', methods=['GET'])
def get_order_tgId(order_id):
    """Возвращаение заказ по указанному tg id """
    try:
        orders = load_orders()
        order = next((o for o in orders if o['tgid'] == order_id), None)

        if order:
            return jsonify({
                "status": "success",
                "order": order
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": f"Order with ID {order_id} not found"
            }), 404

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



@app.route('/get_order_id/<int:order_id>', methods=['GET'])
def get_order_id(order_id):
    """Возвращение заказа по указанному id"""
    try:
        orders = load_orders()
        order = next((o for o in orders if o['id'] == order_id), None)

        if order:
            return jsonify({
                "status": "success",
                "order": order
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": f"Order with ID {order_id} not found"
            }), 404

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



@app.route('/get_all_orders', methods=['GET'])
def get_all_orders():
    """Возвращение всех заказов"""
    try:
        orders = load_orders()
        return jsonify({
            "status": "success",
            "count": len(orders),
            "orders": orders
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500





@app.route('/delete_order_id/<int:order_id>', methods=['DELETE'])
def delete_order_id(order_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем существование заказа
        cursor.execute("SELECT id FROM orders WHERE id = %s", (order_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Order not found'}), 404

        # Удаляем заказ
        cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
        conn.commit()

        return jsonify({'message': f'Order with id {order_id} deleted successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/delete_order_tgid/<int:tgid>', methods=['DELETE'])
def delete_order_tgid(tgid):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем существование заказа
        cursor.execute("SELECT tgid FROM orders WHERE tgid = %s", (tgid,))
        if not cursor.fetchone():
            return jsonify({'error': 'Order with this tgid not found'}), 404

        # Удаляем заказ
        cursor.execute("DELETE FROM orders WHERE tgid = %s", (tgid,))
        conn.commit()

        return jsonify({'message': f'Order with tgid {tgid} deleted successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/update_order/<int:order_id>', methods=['PATCH'])
def update_order(order_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем существование заказа
        cursor.execute("SELECT id FROM orders WHERE id = %s", (order_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Order not found'}), 404

        # Собираем поля для обновления
        update_fields = []
        update_values = []

        for field in ['tgid', 'username', 'ordertext', 'status', 'count', 'price', 'location']:
            if field in data:
                update_fields.append(sql.Identifier(field))
                update_values.append(data[field])

        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400

        # Добавляем order_id в конец значений
        update_values.append(order_id)

        # Строим динамический запрос
        query = sql.SQL("UPDATE orders SET {} WHERE id = %s").format(
            sql.SQL(", ").join(
                sql.SQL("{} = %s").format(field) for field in update_fields
            )
        )

        cursor.execute(query, update_values)
        conn.commit()

        return jsonify({'message': f'Order with id {order_id} updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()





@app.route('/clear_orders', methods=['DELETE'])
def clear_orders():
    """Полностью очищает файл с заказами"""
    try:
        with open(ORDERS_FILE, 'w') as f:
            json.dump([], f)

        return jsonify({
            "status": "success",
            "message": "All orders have been cleared",
            "remaining_orders": []
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to clear orders: {str(e)}"
        }), 500

# "paid" | "passed" / "denied" / "delivered";
@app.route('/filter', methods=['GET'])
def get_products():
    kv = {}
    for key, value in request.args.items():
        kv[key] = value
    data = load_orders()
    filters = list(sorted(data, key=lambda x: x['id']))
    for i in kv.keys():
        if key_in_dictionary(kv, i):
            filters = list(filter(lambda p: p[i] == kv[i], filters))
    return jsonify(filters)





if __name__ == '__main__':
#    app.run(debug=False, host="192.168.8.38")
#    app.run(debug=False, host="192.168.1.68")
    app.run(debug=True)