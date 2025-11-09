from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import numpy as np
from nomic import embed
import torch
import torch.nn.functional as F
from transformers import AutoImageProcessor, AutoModel
from PIL import Image
import threading
from openseas_api import getnftsfromcollection, getcollections, getslugsfromcollections, getbestlisting

# load model for image embeddings
vision_processor = AutoImageProcessor.from_pretrained("nomic-ai/nomic-embed-vision-v1.5")
vision_model = AutoModel.from_pretrained("nomic-ai/nomic-embed-vision-v1.5", trust_remote_code=True)
vision_model.eval()

def embed_text_chunk_local(text: str, 
                           model: str = "nomic-embed-text-v1.5", 
                           inference_mode: str = "local", task_type: 
                           str = "search_document", 
                           dimensionality: int = None) -> np.ndarray: 
    """ Embeds a text chunk and returns its embedding vector. """ 
    kwargs = { "texts": [text], 
              "model": model, 
              "inference_mode": inference_mode, 
              "task_type": task_type } 
    
    if dimensionality is not None: 
        kwargs["dimensionality"] = dimensionality 

    output = embed.text(**kwargs) 
    embeddings = np.array(output["embeddings"]) 
    return embeddings[0]

def embed_image_local(image_path: str) -> torch.Tensor:
    image = Image.open(image_path).convert("RGB")
    inputs = vision_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        output = vision_model(**inputs)
        emb = output.last_hidden_state[:, 0]
        emb_norm = F.normalize(emb, p=2, dim=1)
    return emb_norm.squeeze(0).cpu()

def cosine_similarity(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def collect_nft_data():
    collections = getcollections()
    collection_slugs = getslugsfromcollections(collections)

    nfts = []
    for slug in collection_slugs:
        nfts += getnftsfromcollection(slug)

    # collection_id, nft_id, price, currency, image_url, description
    with app.app_context():
        update_database(nfts)

    return 

def update_database(data):
    # load data from database
    nfts = NFTS.query.all()

    duplicate_map = {}
    # clear database and read exising values into a map
    for nft in nfts:
        duplicate_map[(nft.collection_id, nft.nft_id)] = nft
        db.session.delete(nft)
    

    db.session.commit()

    # add new values (json) into database
    for nft in data:
        if (nft["collection_id"], nft["nft_id"]) in duplicate_map:
            db.session.add(duplicate_map[(nft["collection_id"], nft["nft_id"])])
        else:
            new_nft = NFTS(
                collection_id = nft["collection_id"],
                nft_id = nft["nft_id"],
                price = nft["price"],
                currency = nft["currency"],
                image_embedding_vector = embed_image_local(nft["image_url"]).numpy().astype(float).tolist(),
                text_embedding_vector = embed_text_chunk_local(nft["description"]).numpy().astype(float).tolist()

            )
            db.session.add(new_nft)

    db.session.commit()
    
    global cache_lock
    cache_lock = False

    return

def fill_nft_cache():
    thread = threading.Thread(target=collect_nft_data) # call collect_nft_data on separate thread
    thread.daemon = True   # ensures thread exits when main process exits
    thread.start()
    return

# setup app
app = Flask(__name__)
CORS(app)

# load environment variables
load_dotenv()

# dataase stuff
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL") # port: 5432
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# cache stuff
nft_cache_size = 100
cache_lock = False

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
        return f"Order({self.order_id}, {self.time}, {self.wallet}, {self.funds}, {self.price_cap}, {self.time_interval}, {len(self.preferences_vector)})"
    

class NFTS(db.Model):
    __tablename__ = "nfts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    collection_id = db.Column(db.String(120), nullable=False)
    nft_id = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(120), nullable=False)
    image_embedding_vector = db.Column(db.ARRAY(db.Float)) 
    text_embedding_vector = db.Column(db.ARRAY(db.Float))

    def __repr__(self):
        return f"Order({self.id}, {self.collection_id}, {self.nft_id}, {len(self.image_embedding_vector)}, {len(self.text_embedding_vector)})"


# create table (does nothing if already there)
with app.app_context():
    db.create_all()


# form route
@app.route('/api/form', methods=['POST'])
def index():
    data = request.json

    # TODO: unpack data and make sure its a json with the following fields
    # json should be of form {wallet, funds, price_cap, time_interval, preferences_vector}
   

    new_order = Orders(
        time=datetime.now(timezone.utc) + timedelta(days=data["time_interval"]), # add interval to this
        wallet=data["wallet"],
        funds=data["funds"], # funds in what?
        price_cap=data["price_cap"],
        time_interval=data["time_interval"], # days for now
        preferences_vector=embed_text_chunk_local(data["preferences_vector"]).numpy().astype(float).tolist()
    )

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
        db.session.delete(i)
        
        # call buy function
        buy(i)

        # add back if there are funds left
        if i.funds > i.price_cap:
            i.funds -= i.price_cap
            i.time = now + timedelta(days=i.time_interval) # new time for next buy
            db.session.add(i)
    db.session.commit()


    return jsonify({"message": f"ordered {len(orders)}"}), 200

def buy(order):
    global cache_lock

    # get amounts to spend
    if order.funds < order.price_cap:
        funds = order.funds
    else:
        funds = order.price_cap
    
    # TODO: some sort of currency conversion?
    
    # load data from database
    nfts = NFTS.query.all()

    # if there is no data, call the collect data funtion synchronously
    if len(nfts) == 0:
        collect_nft_data()

    # make sure there are more than cache size
    if len(nfts) < nft_cache_size and not cache_lock:
        cache_lock = True
        fill_nft_cache() # call collect_nft_data on separate thread

    # iterate and find the closes to data
    max_similarity = 0
    best_nft = None

    for nft in nfts:
        # make sure there are enough funds
        if nft.price <= funds:

            # get similarity of image and text embeddings vectors
            if nft.image_embedding_vector:
                similarity_image = cosine_similarity(order.preferences_vector, nft.image_embedding_vector)
            else:
                similarity_image = None

            if nft.text_embedding_vector:
                similarity_text = cosine_similarity(order.preferences_vector, nft.text_embedding_vector)
            else:
                similarity_text = None

            # take average similarity score
            if similarity_image and similarity_text:
                similarity = (similarity_image + similarity_text) / 2
            elif similarity_image:
                similarity = similarity_image
            elif similarity_text:
                similarity = similarity_text
            else:
                similarity = 0
            
            # replace if better
            if similarity > max_similarity:
                max_similarity = similarity
                best_nft = nft
    
    # if there is no nft to buy, get more options
    if best_nft is None:
        collect_nft_data()  # get nfts syncronously
        buy(order)
        return

    # delete nft
    db.session.delete(best_nft)
    db.session.commit()

    # vefify that there is a nft to buy and there are enough funds
    currency, value = getbestlisting(best_nft.collection_id, best_nft.nft_id)
    if (currency == "Error" or value == 0) or value > funds:
        buy(order) # if not recursivly call buy function again
        return

    # TODO: submit order

    # TODO: send them a email or something





if __name__ == '__main__':
    app.run(debug=True)
