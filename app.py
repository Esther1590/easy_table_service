# app.py
from flask import Flask, request, jsonify, render_template
from models import db, User, Menu, Order, Payment
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///easy_table_service.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize the SQLAlchemy instance with the Flask app
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

def create_tables():
    with app.app_context():
        try:
            db.create_all()
            if os.path.exists('easy_table_service.db'):
                print("Database file exists")
            else:
                print("Database file does not exist")
            print("Tables created successfully")  # Debug statement

            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables in database: {tables}")  # List tables

            # Additional debug statements
            print(f"User class table name: {User.__table__}")
            print(f"Menu class table name: {Menu.__table__}")
            print(f"Order class table name: {Order.__table__}")
            print(f"Payment class table name: {Payment.__table__}")
        except Exception as e:
            print(f"Error creating tables: {e}")  # Detailed error message

# Ensure tables are created only once using the application context
create_tables()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu', methods=['GET', 'POST'])
def manage_menu():
    try:
        if request.method == 'POST':
            data = request.json
            new_item = Menu(item_name=data['item_name'], description=data.get('description'), price=data['price'])
            db.session.add(new_item)
            db.session.commit()
            return jsonify({'message': 'Menu item added'}), 201
        else:
            menu = Menu.query.all()
            print("Fetched menu items:", menu)  # Debug statement
            return jsonify([{'id': item.id, 'item_name': item.item_name, 'description': item.description, 'price': item.price} for item in menu])
    except Exception as e:
        app.logger.error(f"Error handling /menu request: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/order', methods=['POST'])
def create_order():
    try:
        data = request.json
        new_order = Order(user_id=data['user_id'], total_amount=data['total_amount'], status='Pending')
        db.session.add(new_order)
        db.session.commit()
        return jsonify({'message': 'Order created', 'order_id': new_order.id}), 201
    except Exception as e:
        app.logger.error(f"Error handling /order request: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/payment', methods=['POST'])
def process_payment():
    try:
        data = request.json
        new_payment = Payment(order_id=data['order_id'], amount=data['amount'], payment_method=data['payment_method'])
        order = Order.query.get(data['order_id'])
        order.status = 'Paid'
        db.session.add(new_payment)
        db.session.commit()
        return jsonify({'message': 'Payment processed'}), 201
    except Exception as e:
        app.logger.error(f"Error handling /payment request: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
