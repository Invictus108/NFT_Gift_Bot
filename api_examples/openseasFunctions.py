import os, requests, json
from dotenv import load_dotenv

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
    return requests.get(url, headers=headers).json()['orders'][1]['maker_asset_bundle']

"""
https://docs.opensea.io/reference/list_collections

----getcollections---- >>> returns a list of collections

Possible chains:
abstract, ape_chain, arbitrum, arbitrum_nova, avalanche, b3,
base, bera_chain, blast, ethereum, flow, klaytn, matic, optimism,
ronin, shape, solana, soneium, unichain, zora 

Possible order_by:
created_date, market_cap, num_owners, one_day_change, seven_day_change, 
seven_day_volume
"""

def getcollections(num=100, order_by=None, chain=None, include_hidden=False, creator_username=None):
    url = "https://api.opensea.io/api/v2/collections?"
    if chain: url += f"chain={chain}&"
    if order_by: url += f"order_by={order_by}&"
    if creator_username: url += f"creator_username={creator_username}&"
    url += f"limit={num}&"
    url += f"include_hidden=true&" if include_hidden else f"include_hidden=false&"

    return requests.get(url, headers=headers).json()["collections"]

"""
----getslugsfromcollections---- given a list of collections (which is conveniently returned by getcollections), return their collection_slugs
"""

def getslugsfromcollections(collections):
    return [collection['collection'] for collection in collections]

"""
https://docs.opensea.io/reference/list_nfts_by_collection
----getnftsfromcollection---- >>>> given a collection_slug, returns a list of nfts
"""

def getnftsfromcollection(collection_slug, limit=100):
    url = f"https://api.opensea.io/api/v2/collection/{collection_slug}/nfts"
    url += f"?limit={limit}"
    return requests.get(url, headers=headers).json()['nfts']

"""
https://docs.opensea.io/reference/get_all_listings_on_collection_v2
----getnftsfromcollection---- >>>> given a collection_slug, returns a list of listings
"""

def getlistingsfromcollection(collection_slug, limit=100):
    url = f"https://api.opensea.io/api/v2/listings/collection/{collection_slug}/all"
    url += f"?limit={limit}"
    return requests.get(url, headers=headers).text

"""
---getnftdata---- >>>> given an nft (likely returned from getnftsfromcollection, returns a dictionary that contains the more useful data

id and collection for getting best listing
desc, image, and is_nsfw to match customer preferences
"""

def getnftdata(nft):
    return {
        "identifier" : nft['identifier'],
        "collection" : nft['collection'],
        "name": nft['name'],
        "description": nft['description'],
        "image_url" : nft['image_url'],
        "is_nsfw" : nft['is_nsfw']
    }

#gets best listing by an nft

def getbestlisting(nft):
    url = f"https://api.opensea.io/api/v2/listings/collection/{nft['collection']}/nfts/{nft["identifier"]}/best"
    return requests.get(url, headers=headers).json()