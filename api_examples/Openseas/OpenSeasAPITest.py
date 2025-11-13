import os, requests, json
from dotenv import load_dotenv
import random

load_dotenv()
API_KEY = os.getenv('API_KEY')

headers = {
    "accept": "application/json",
    "x-api-key": API_KEY
}

"""
https://docs.opensea.io/reference/list_collections

----getlistings---- >>> returns a string of listings, given a chain

Possible chains:
abstract, ape_chain, arbitrum, arbitrum_nova, avalanche, b3,
base, bera_chain, blast, ethereum, flow, klaytn, matic, optimism,
ronin, shape, solana, soneium, unichain, zora 

"""
def getlistings(chain):
     url = f"https://api.opensea.io//api/v2/orders/{chain}/seaport/listings"
     return requests.get(url, headers=headers).json()['orders']
#
# def getlistingprice(listing):
#     return listing['current_price']
#
# def getlistingprices(chain):
#     return [getlistingprice(listing) for listing in getlistings(chain)["orders"]]


# Pure API Endpoint
def getcollections(num=100, order_by="market_cap", chain="ethereum"):
    url = "https://api.opensea.io/api/v2/collections?"
    if chain: url += f"chain={chain}&"
    if order_by: url += f"order_by={order_by}&"
    if num: url += f"limit={num}&"

    return requests.get(url, headers=headers).json()

def getslugsfromcollections(collections):
    return [collection['collection'] for collection in collections]

def getbestcollectionprice(collection_slug, num=100):
    url = "https://api.opensea.io/api/v2/listings/collection/collection_slug/best"


print(getlistings("ethereum")[0])