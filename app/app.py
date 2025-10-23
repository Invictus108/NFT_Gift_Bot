from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timezone, timedelta
from sentence_transformers import SentenceTransformer

# setup app
app = Flask(__name__)
CORS(app)

# dataase stuff
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("database_url") # port: 5432
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create database
db = SQLAlchemy(app)

class Orders(db.Model):
    __tablename__ = "orders"
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.DateTime, nullable=False)
    wallet = db.Column(db.String(120), nullable=False)
    funds = db.Column(db.Float, nullable=False)
    price_cap = db.Column(db.Float)
    time_interval = db.Column(db.Integer)  # gotta figure out what unit
    preferences_vector = db.Column(db.ARRAY(db.Float))  # array of floats


# create table (does nothing if already there)
with app.app_context():
    db.create_all()


# form route
@app.route('/api/form', methods=['POST'])
def index():
    data = request.json

    # TODO: unpack data and make sure its a json with the following fields

    # define model
    model = SentenceTransformer('intfloat/e5-small-v2')

    new_order = Orders(
        time=datetime.now(timezone.utc) + timedelta(days=data["time_interval"]), # add interval to this
        wallet=data["wallet"],
        funds=data["funds"], # funds in what?
        price_cap=data["price_cap"],
        time_interval=data["time_interval"], # days for now
        preferences_vector=model.encode(data["preferences_vector"])
    )

    db.session.add(new_order)
    db.session.commit()

    return data

# this is the function to check if there are any valid orders when pinged
@app.route('/api/check_orders', methods=['GET'])
def check_orders():
    # get time
    now = datetime.now(timezone.utc)

    # find all orders that need to be fulfilled 
    past_entries = Orders.query.filter(Orders.time < now).all()

    for i in past_entries:
        db.session.delete(i)
        buy(i)

        # add back if there are funds left
        if i.funds > i.price_cap:
            i.funds -= i.price_cap
            i.time = now + timedelta(days=i.time_interval) # new time for next buy
            db.session.add(i)
            db.session.commit()


    return "done"

def buy(order):
    # get amounts to spend
    if order.funds < order.price_cap:
        funds = order.funds
    else:
        funds = order.price_cap
    

    # TODO: get options and data from APIS

    # TODO: AI stuff to decide on thing

    # TODO: submit order

    # TODO: send them a email or something
        
    pass
