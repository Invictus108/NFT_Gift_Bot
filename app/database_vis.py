from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ARRAY, Text
import os
from dotenv import load_dotenv

# ------------------
# SQLAlchemy Setup
# ------------------
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


# ------------------
# Orders Model
# ------------------

class Orders(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False)
    time = Column(DateTime, nullable=False)
    wallet = Column(String(120), nullable=False)
    funds = Column(Float, nullable=False)
    price_cap = Column(Float)
    time_interval = Column(Integer)
    preferences_vector = Column(ARRAY(Float))

    def __repr__(self):
        size = len(self.preferences_vector) if self.preferences_vector else 0
        return (
            f"Order(id={self.order_id}, name={self.name}, email={self.email}, "
            f"time={self.time}, wallet={self.wallet}, funds={self.funds}, "
            f"price_cap={self.price_cap}, time_interval={self.time_interval}, "
            f"preferences_len={size})"
        )
    

class NFTS(Base):
    __tablename__ = "nfts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Text, nullable=False)
    nft_id = Column(Text, nullable=False)
    image_url = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(Text, nullable=False)
    image_embedding_vector = Column(ARRAY(Float))
    text_embedding_vector = Column(ARRAY(Float))

    def __repr__(self):
        image_size = len(self.image_embedding_vector) if self.image_embedding_vector else 0
        text_size = len(self.text_embedding_vector) if self.text_embedding_vector else 0

        return (
            f"NFT(id={self.id}, collection_id={self.collection_id}, nft_id={self.nft_id}, "
            f"image_emb_len={image_size}, text_emb_len={text_size})"
        )


# ------------------
# Query + Print
# ------------------

def list_all_orders():
    print("\nFetching all orders...\n")
    orders = session.query(NFTS).all()

    if not orders:
        print("No orders found.")
        return

    for order in orders:
        print(order)

    print("\nDone.\n")


if __name__ == "__main__":
    list_all_orders()
