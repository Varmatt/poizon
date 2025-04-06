from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
ORDERS_FILE = 'orders.json'


# Загружаем существующих пользователей или создаем пустой список
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            return json.load(f)
    return []


# Сохраняем пользователей в файл
def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=4)


# Генерируем новый ID
def generate_id(orders):
    if not orders:
        return 1
    return max(order['id'] for order in orders) + 1


@app.route('/add_order', methods=['GET'])
def add_orders():
    user_data = request.get_json()
    if not user_data:
        return jsonify({'error': 'No JSON data provided'}), 400
    orders = load_orders()
    new_id = generate_id(orders)
    user_data['id'] = new_id
    orders.append(user_data)
    save_orders(orders)
    return jsonify({'message': 'User added successfully', 'id': new_id}), 200


@app.route('/delete_order_id/<int:order_id>', methods=['DELETE'])
def delete_order_id(order_id):
    """Удаляет товар по ID"""
    try:
        # Загружаем текущие товары
        orders = load_orders()

        # Находим индекс товара с указанным ID
        order_index = None
        for i, order in enumerate(orders):
            if order.get('id') == order_id:
                order_index = i
                break

        # Если товар не найден
        if order_index is None:
            return jsonify({
                "status": "error",
                "message": f"Product with ID {order_id} not found"
            }), 404

        # Удаляем товар
        deleted_order = orders.pop(order_index)

        # Сохраняем обновленный список
        save_orders(orders)

        return jsonify({
            "status": "success",
            "message": f"Product with ID {order_id} deleted",
            "deleted_product": deleted_order
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/get_order_tgId/<int:order_id>', methods=['GET'])
def get_ordertg(order_id):
    """Возвращает заказ по указанному ID"""
    try:
        orders = load_orders()

        # Ищем заказ с указанным ID
        order = next((o for o in orders if o['tgId'] == order_id), None)

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
    """Возвращает заказ по указанному ID"""
    try:
        orders = load_orders()

        # Ищем заказ с указанным ID
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
    """Возвращает все заказы"""
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


@app.route('/delete_order_tgId/<int:order_id>', methods=['DELETE'])
def delete_order_tgId(order_id):
    try:
        orders = load_orders()
        order_index = None
        for i, order in enumerate(orders):
            if order.get('tgId') == order_id:
                order_index = i
                break
        if order_index is None:
            return jsonify({
                "status": "error",
                "message": f"Product with tg ID {order_id} not found"
            }), 404
        deleted_order = orders.pop(order_index)
        save_orders(orders)
        return jsonify({
            "status": "success",
            "message": f"Product with ID {order_id} deleted",
            "deleted_product": deleted_order
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



@app.route('/clear_orders', methods=['DELETE'])
def clear_orders():
    """Полностью очищает файл с заказами"""
    try:
        # Перезаписываем файл пустым списком
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


if __name__ == '__main__':
    app.run(debug=False, host="192.168.1.68")
#    app.run(debug=True)