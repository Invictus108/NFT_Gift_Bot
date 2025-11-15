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
from PIL import Image, UnidentifiedImageError
import threading
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from openseas_api import getnftsfromcollection, getcollections, getslugsfromcollections, getbestlisting
from multipipline_api import getNftWithPriceCeling

# load model for image embeddings
vision_processor = AutoImageProcessor.from_pretrained("nomic-ai/nomic-embed-vision-v1.5")
vision_model = AutoModel.from_pretrained("nomic-ai/nomic-embed-vision-v1.5", trust_remote_code=True)
vision_model.eval()

# helper funtions
def interval_to_days(interval: str) -> int:
    """Convert 'Daily', 'Weekly', 'Bi-weekly', 'Monthly' into days."""
    interval = (interval or "").strip().lower()

    if interval == "daily":
        return 1
    elif interval == "weekly":
        return 7
    elif interval in ("bi-weekly", "biweekly"):
        return 14
    elif interval == "monthly":
        return 30   # approximate, you can choose 30 or 31
    else:
        raise ValueError(f"Unknown interval: {interval}")

def embed_text_chunk_local(text: str, 
                           model: str = "nomic-embed-text-v1.5", 
                           inference_mode: str = "local", task_type: 
                           str = "search_document", 
                           dimensionality: int = None) -> np.ndarray: 
    """ Embeds a text chunk and returns its embedding vector. """ 
    print("ebeding text")
    kwargs = { "texts": [text], 
              "model": model, 
              "inference_mode": inference_mode, 
              "task_type": task_type } 
    
    if dimensionality is not None: 
        kwargs["dimensionality"] = dimensionality 

    output = embed.text(**kwargs) 
    embeddings = np.array(output["embeddings"]) 
    return embeddings[0]

def rasterize_svg_simple(svg_bytes):
    """
    Very simple fallback: extract <image href='...'> from SVG 
    and rasterize THAT instead.
    """
    try:
        soup = BeautifulSoup(svg_bytes.decode("utf-8"), "xml")
        img_tag = soup.find("image")
        if img_tag and img_tag.get("href"):
            img_url = img_tag["href"]
            r = requests.get(img_url, timeout=10)
            inner = Image.open(BytesIO(r.content)).convert("RGB")
            return inner
    except:
        pass

    return None  # fallback handled by caller


def embed_image_local(image_path: str) -> torch.Tensor:
    print("embedding image")

    # ---- HTTP remote images ----
    if image_path.startswith("http"):
        try:
            r = requests.get(image_path, timeout=10)
            r.raise_for_status()
            data = r.content

            # -------- Handle SVG without Cairo --------
            if image_path.lower().endswith(".svg"):
                print("SVG detected → attempting lightweight rasterization")

                # Try simple rasterization of <image> tags
                fallback = rasterize_svg_simple(data)
                if fallback:
                    img = fallback
                else:
                    print("SVG cannot be rasterized → using blank vector")
                    return torch.zeros(768)

            else:
                # -------- Normal raster image --------
                try:
                    img = Image.open(BytesIO(data)).convert("RGB")
                except UnidentifiedImageError:
                    print(f"Unrecognized image format: {image_path}")
                    return torch.zeros(768)

        except Exception as e:
            print(f"Failed to load remote image {image_path}: {e}")
            return torch.zeros(768)

    # ---- Local file images ----
    else:
        try:
            if image_path.lower().endswith(".svg"):
                print("Local SVG detected → attempting lightweight rasterization")

                with open(image_path, "rb") as f:
                    data = f.read()

                fallback = rasterize_svg_simple(data)
                if fallback:
                    img = fallback
                else:
                    print("SVG cannot be rasterized → using blank vector")
                    return torch.zeros(768)
            else:
                img = Image.open(image_path).convert("RGB")

        except Exception as e:
            print(f"Failed to load local image {image_path}: {e}")
            return torch.zeros(768)

    # ---- Embed ----
    inputs = vision_processor(images=img, return_tensors="pt")
    with torch.no_grad():
        output = vision_model(**inputs)
        emb = output.last_hidden_state[:, 0]
        emb_norm = F.normalize(emb, p=2, dim=1)

    return emb_norm.squeeze(0).cpu()

def cosine_similarity(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    return np.dot(v1, v2) 

def collect_nft_data():
    # collections = getcollections()
    # collection_slugs = getslugsfromcollections(collections)

    # nfts = []
    # for slug in collection_slugs:
    #     nfts += getnftsfromcollection(slug)

    print("collectiong data from openseas api")

    nfts = getNftWithPriceCeling(10)

    # collection_id, nft_id, price, currency, image_url, description
    with app.app_context():
        update_database(nfts)

    return 

def update_database(data):
    print("recived data and am updating databsase")
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
        collection_id = nft.get("collection_id")
        # check if its a string
        if not isinstance(collection_id, str):
            print("no collection ID")
            continue

        nft_id = nft.get("nft_id")

        if (collection_id, nft_id) in duplicate_map:
            db.session.add(duplicate_map[(collection_id, nft_id)])
        else:
            image_url = nft.get("image_url", "")
            description = nft.get("description", "")

            new_nft = NFTS(
                collection_id = collection_id,
                nft_id = str(nft_id),
                price = nft.get("price"),
                currency = nft.get("currency"),

                image_embedding_vector = (
                    None if not image_url 
                    else embed_image_local(image_url).numpy().astype(float).tolist()
                ),

                text_embedding_vector = (
                    None if not description 
                    else embed_text_chunk_local(description).astype(float).tolist()
                ),
            )

        db.session.add(new_nft)


    db.session.commit()
    
    global cache_lock
    cache_lock = False

    return

def fill_nft_cache():
    print("async fill called")
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
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    wallet = db.Column(db.String(120), nullable=False)
    funds = db.Column(db.Float, nullable=False)
    price_cap = db.Column(db.Float)
    time_interval = db.Column(db.Integer)  # gotta figure out what unit
    preferences_vector = db.Column(db.ARRAY(db.Float))  # array of floats

    def __repr__(self):
        return f"Order({self.order_id}, {self.name}, {self.time}, {self.wallet}, {self.funds}, {self.price_cap}, {self.time_interval}, {len(self.preferences_vector)})"
    

class NFTS(db.Model):
    __tablename__ = "nfts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    collection_id = db.Column(db.String(120), nullable=False)
    nft_id = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(120), nullable=False)
    image_embedding_vector = db.Column(db.ARRAY(db.Float)) 
    text_embedding_vector = db.Column(db.ARRAY(db.Float))

    def __repr__(self):
        return f"NFT({self.id}, {self.collection_id}, {self.nft_id}, {len(self.image_embedding_vector)}, {len(self.text_embedding_vector)})"


# create table (does nothing if already there)
with app.app_context():
    db.create_all()


# form route
@app.route('/api/form', methods=['POST'])
def index():
    data = request.json

    # Extract fields
    wallet = data.get("walletInfo", {}).get("walletAddress")
    funds = data.get("budget", {}).get("totalBudget")
    price_cap = data.get("budget", {}).get("maxPricePerNFT")
    time_interval = interval_to_days(data.get("budget", {}).get("frequency"))
    name = data.get("personalInfo", {}).get("fullName")
    email = data.get("personalInfo", {}).get("email")
    
    # Build preferences vector
    preferences_block = data.get("preferences", {})

    styles = preferences_block.get("styles", [])
    themes = preferences_block.get("themes", [])
    additional = preferences_block.get("additionalPreferences", "")

    # weight the styles and themes
    styles_weight = 2
    themes_weight = 2

    # create embedded string
    preferences_string = " ".join(styles * styles_weight) + " " + " ".join(themes * themes_weight) + " " + additional

    # create preferences vector
    preferences_vector = embed_text_chunk_local(preferences_string).astype(float).tolist()

    # create new order
    new_order = Orders(
        name=name,
        email=email,
        time=datetime.now(timezone.utc) + timedelta(days=time_interval), # add interval to this
        wallet=wallet,
        funds=funds, 
        price_cap=price_cap,
        time_interval=time_interval, # days for now
        preferences_vector=preferences_vector
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

    print("got order")

    for i in orders:   
        nfts = db.session.query(NFTS).count()
        print(f"nfts length: {nfts}")
        # call buy function
        value = buy(i, nfts+1)

        print(f"got value from buy: {value}")

        if value == "Store Empty":
            continue

        # add back if there are funds left
        if i.funds - value > 0:
            i.funds -= value
            i.time = now + timedelta(days=i.time_interval) # new time for next buy
        else:
            db.session.delete(i)

    db.session.commit()


    return jsonify({"message": f"ordered {len(orders)}"}), 200

def buy(order, max_depth, recursion_level=0):
    print(f"Finding NFT for {order}")
    recursion_level += 1

    if recursion_level > max_depth:
        return "Store Empty"
    
    global cache_lock
    print(f"cache lock: {cache_lock}")

    # get amounts to spend
    if order.funds < order.price_cap:
        funds = order.funds
    else:
        funds = order.price_cap
    
    # TODO: some sort of currency conversion?
    
    # load data from database
    nfts = NFTS.query.all()
    print(f"got nfts of len: {len(nfts)}")

    # if there is no data, call the collect data funtion synchronously
    if len(nfts) == 0:
        if not cache_lock:
            print("empty database... collecting data")
            collect_nft_data()
        else:
            return "Store Empty"

    # make sure there are more than cache size
    if len(nfts) < nft_cache_size and not cache_lock:
        print("below cache size... collecting data")
        cache_lock = True
        fill_nft_cache() # call collect_nft_data on separate thread

    # iterate and find the closes to data
    max_similarity = 0
    best_nft = None
    
    print("starting buy loop")

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
            if similarity_image is not None and similarity_text is not None:
                similarity = (similarity_image + similarity_text) / 2
            elif similarity_image is not None:
                similarity = similarity_image
            elif similarity_text is not None:
                similarity = similarity_text
            else:
                similarity = 0
            
            # replace if better
            if similarity > max_similarity:
                max_similarity = similarity
                best_nft = nft
    
    print(f"found poternial nft: {best_nft}")
    # if there is no nft to buy, get more options
    if best_nft is None:
        print("no nft to buy... collecting data")
        if not cache_lock:
            collect_nft_data()  # get nfts syncronously
        return buy(order, db.session.query(NFTS).count(), recursion_level=recursion_level)

    # delete nft
    db.session.delete(best_nft)
    db.session.commit()

    # vefify that there is a nft to buy and there are enough funds
    currency, value = getbestlisting(best_nft.collection_id, best_nft.nft_id)
    print(f"currency: {currency}, value: {value}")

    if (currency == "Error" or value == 0) or value > funds:
        print("no valid listing for nft")
        return buy(order, db.session.query(NFTS).count(), recursion_level=recursion_level) # if not recursivly call buy function again
        
    print(f"Buying {best_nft.collection_id} {best_nft.nft_id} for {value} {currency}")

    # TODO: submit order

    # TODO: send them a email or something

    return value





if __name__ == '__main__':
    app.run(debug=True)
