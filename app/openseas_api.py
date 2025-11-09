import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')

headers = {
    "accept": "application/json",
    "x-api-key": API_KEY
}

# reformat data as simple json
def getnftdata(nft):
    return {
        "identifier" : nft['identifier'],
        "collection" : nft['collection'],
        "name": nft['name'],
        "description": nft['description'],
        "image_url" : nft['image_url'],
        "is_nsfw" : nft['is_nsfw']
    }

# get best available listing
def getbestlisting(collection_slug, nft):
    url = f"https://api.opensea.io/api/v2/listings/collection/{collection_slug}/nfts/{nft}/best"

    order_json = requests.get(url, headers=headers).json()

    
    # TODO: this is jank
    try:
        price_info = order_json["price"]["current"]
        currency = price_info.get("currency")
        decimals = price_info.get("decimals", 0)
        value_str = price_info.get("value", "0")

        # convert value_str to a decimal number accounting for decimals
        value = int(value_str) / (10 ** decimals)


        return currency, value
    except:
        return "Error", 0

# get the NFTs from the collection and add price and currecy
def getnftsfromcollection(collection_slug, limit=100):
    url = f"https://api.opensea.io/api/v2/collection/{collection_slug}/nfts"
    url += f"?limit={limit}"

    try:
        nfts = requests.get(url, headers=headers).json()['nfts']
    except:
        return []

    # filter out those outside price range (same computation on generating embeddings)
    good_nfts = []

    for nft in nfts:
        currency, value = getbestlisting(nft['collection'], nft["identifier"])

        # catch errors and move on
        if currency == "Error" or value == 0:
            continue

        # get simple nft data
        nft_data = getnftdata(nft)

        # add currency and price fields
        nft_data["currency"] = currency
        nft_data["price"] = value

        # add to return list
        good_nfts.append(nft)

    return good_nfts

# get a list of collections
def getcollections(num=100, order_by="seven_day_volume", chain="ethereum"):
    url = "https://api.opensea.io/api/v2/collections?"
    if chain: url += f"chain={chain}&"
    if order_by: url += f"order_by={order_by}&"
    url += f"limit={num}&"

    return requests.get(url, headers=headers).json()["collections"]

# extract collection ids
def getslugsfromcollections(collections):
    return [collection['collection'] for collection in collections]