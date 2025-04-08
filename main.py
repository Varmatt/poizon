from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)
ORDERS_FILE = 'orders.json'



def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=4)



def generate_id(orders):
    if not orders:
        return 1
    return max(order['id'] for order in orders) + 1


@app.route('/add_order', methods=['POST'])
def add_orders():
    """Добавление товара"""
    user_data = request.get_json()
    if not user_data:
        return jsonify({'error': 'No JSON data provided'}), 400
    orders = load_orders()
    new_id = generate_id(orders)
    user_data['id'] = new_id
    user_data['status'] = ''
    user_data['status'] = ''
    user_data['count'] = -1
    user_data['price'] = -1
    user_data['location'] = ''
    orders.append(user_data)
    save_orders(orders)
    return jsonify({'message': 'User added successfully', 'id': new_id}), 200


@app.route('/delete_order_id/<int:order_id>', methods=['DELETE'])
def delete_order_id(order_id):
    """Удаляение заказа по id"""
    try:
        orders = load_orders()
        order_index = None
        for i, order in enumerate(orders):
            if order.get('id') == order_id:
                order_index = i
                break
        if order_index is None:
            return jsonify({
                "status": "error",
                "message": f"Product with ID {order_id} not found"
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



@app.route('/get_order_tgId/<int:order_id>', methods=['GET'])
def get_order_tgId(order_id):
    """Возвращаение заказ по указанному tg id """
    try:
        orders = load_orders()
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



@app.route('/delete_order_tgId/<int:order_id>', methods=['DELETE'])
def delete_order_tgId(order_id):
    """Удаление заказа по tg id"""
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



@app.route('/update_order/<int:order_id>', methods=['PATCH'])
def update_order(order_id):
    """Обновлние заказ по ID"""
    update_data = request.get_json()
    if not update_data:
        return jsonify({'error': 'No data provided'}), 400
    orders = load_orders()
    order_found = False
    for order in orders:
        if order['id'] == order_id:
            for key, value in update_data.items():
                if key in order:
                    order[key] = value
            order_found = True
            break

    if not order_found:
        return jsonify({'error': 'Order not found'}), 404
    save_orders(orders)

    return jsonify({'message': 'Order updated successfully'}), 200






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


if __name__ == '__main__':
#    app.run(debug=False, host="192.168.8.38")
    app.run(debug=False, host="192.168.1.68")
#    app.run(debug=True)