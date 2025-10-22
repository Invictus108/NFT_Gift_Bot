from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

# setup app
app = Flask(__name__)
CORS(app)

# dataase stuff
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("database_url")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create database
db = SQLAlchemy(app)

class Orders(db.Model):
    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer) 
    time = db.Column(db.DateTime, nullable=False)
    wallet = db.Column(db.String(120), nullable=False)
    funds = db.Column(db.Float, nullable=False)
    price_cap = db.Column(db.Float)
    time_interval = db.Column(db.Integer)  # gotta figure out what unit
    preferences_vector = db.Column(db.ARRAY(db.Float))  # array of floats

    def __repr__(self):
        return f"<UserSettings user_id={self.user_id} wallet={self.wallet}>"

# create table (does nothing if already there)
with app.app_context():
    db.create_all()


# form route
@app.route('/api/form', methods=['POST'])
def index():
    data = request.json

    # TODO: unpack data
    # TODO: create embedding vector
    # TODO: add data to database

    # TODO: these are just placeholder values for now
    new_order = Orders(
        user_id=0,
        time=datetime.utcnow(), # add interval to this
        wallet="0xABC123",
        funds=1000.0,
        price_cap=250.0,
        time_interval=30,
        preferences_vector=[0.2, 0.5, 0.3]
    )

    db.session.add(new_order)
    db.session.commit()

    return data

# this is the function to check if there are any valid orders when pinged
@app.route('/api/check_orders', methods=['GET'])
def check_orders():
    # get time
    now = datetime.utcnow()

    # find all orders that need to be fulfilled 
    past_entries = Orders.query.filter(Orders.time < now).all()

    for i in past_entries:
        buy(i)
        # TODO: insert back into datbase if they have funds left

    return "done"

def buy(order):
    # TODO: buy order
    pass
