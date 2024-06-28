from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///easy_table_service.db'
db = SQLAlchemy(app)

# Import models after initializing the db
from models import User, Menu, Order, Payment

def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu', methods=['GET', 'POST'])
def manage_menu():
    if request.method == 'POST':
        data = request.json
        new_item = Menu(item_name=data['item_name'], description=data.get('description'), price=data['price'])
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'message': 'Menu item added'}), 201
    else:
        menu = Menu.query.all()
        return jsonify([{'id': item.id, 'item_name': item.item_name, 'description': item.description, 'price': item.price} for item in menu])

@app.route('/order', methods=['POST'])
def create_order():
    data = request.json
    new_order = Order(user_id=data['user_id'], total_amount=data['total_amount'], status='Pending')
    db.session.add(new_order)
    db.session.commit()
    return jsonify({'message': 'Order created', 'order_id': new_order.id}), 201

@app.route('/payment', methods=['POST'])
def process_payment():
    data = request.json
    new_payment = Payment(order_id=data['order_id'], amount=data['amount'], payment_method=data['payment_method'])
    order = Order.query.get(data['order_id'])
    order.status = 'Paid'
    db.session.add(new_payment)
    db.session.commit()
    return jsonify({'message': 'Payment processed'}), 201

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)

