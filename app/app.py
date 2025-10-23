from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timezone, timedelta
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# setup app
app = Flask(__name__)
CORS(app)

# load environment variables
load_dotenv()

# dataase stuff
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL") # port: 5432
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

    def __repr__(self):
        return f"Order({self.order_id}, {self.time}, {self.wallet}, {self.funds}, {self.price_cap}, {self.time_interval}, {self.preferences_vector})"


# create table (does nothing if already there)
with app.app_context():
    db.create_all()


# form route
@app.route('/api/form', methods=['POST'])
def index():
    data = request.json

    # TODO: unpack data and make sure its a json with the following fields
    # json should be of form {wallet, funds, price_cap, time_interval, preferences_vector}

    # define model
    model = SentenceTransformer('intfloat/e5-small-v2')

    new_order = Orders(
        time=datetime.now(timezone.utc) + timedelta(days=data["time_interval"]), # add interval to this
        wallet=data["wallet"],
        funds=data["funds"], # funds in what?
        price_cap=data["price_cap"],
        time_interval=data["time_interval"], # days for now
        preferences_vector=model.encode(data["preferences_vector"]).astype(float).tolist()
    )

    with app.app_context():
        db.session.add(new_order)
        db.session.commit()

    return jsonify({"message": "success"}), 200

# this is the function to check if there are any valid orders when pinged
@app.route('/api/check_orders', methods=['GET'])
def check_orders():
    # get time
    now = datetime.now(timezone.utc)

    # find all orders that need to be fulfilled 
    orders = Orders.query.filter(Orders.time < now).all()

    for i in orders:
        with app.app_context():
            db.session.delete(i)
            db.session.commit()
        
        # call buy function
        buy(i)

        # add back if there are funds left
        if i.funds > i.price_cap:
            i.funds -= i.price_cap
            i.time = now + timedelta(days=i.time_interval) # new time for next buy
            with app.app_context():
                db.session.add(i)
                db.session.commit()


    return jsonify({"message": f"ordered {len(orders)}"}), 200

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
        



if __name__ == '__main__':
    app.run(debug=True)
