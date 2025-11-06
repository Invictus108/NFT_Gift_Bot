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

# this is kinda useless
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

# TODO: figure out why this dosent work. 
# TODO: price filtering here? Would make things easier
def getcollections(num=100, order_by=None, chain="ethereum"):
    url = "https://api.opensea.io/api/v2/collections?"
    if chain: url += f"chain={chain}&"
    if order_by: url += f"order_by={order_by}&"
    url += f"limit={num}&"

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

# find listing and return best price in ETH
# TODO: look through all listing to check if there is one in ETH
# right now its just returning the first one even if its not in ETH
def getbestlisting(nft):
    url = f"https://api.opensea.io/api/v2/listings/collection/{nft['collection']}/nfts/{nft["identifier"]}/best"

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


# get the NFTs from the collection and filter them 
def getnftsfromcollection(collection_slug, max_price, limit=100):
    url = f"https://api.opensea.io/api/v2/collection/{collection_slug}/nfts"
    url += f"?limit={limit}"

    nfts = requests.get(url, headers=headers).json()['nfts']

    # filter out those outside price range (same computation on generating embeddings)
    good_nfts = []

    for nft in nfts:
        currency, value = getbestlisting(nft)
        if currency == "ETH" and value <= max_price:
            print(currency, value)
            good_nfts.append(nft)

    return good_nfts


"""
https://docs.opensea.io/reference/get_all_listings_on_collection_v2
----getnftsfromcollection---- >>>> given a collection_slug, returns a list of listings
"""

# would this be more effiecnt then getting individual NFT listings?
# does it return the needed data on the NFTS or just the listings
def getlistingsfromcollection(collection_slug, limit=100):
    url = f"https://api.opensea.io/api/v2/listings/collection/{collection_slug}/all"
    url += f"?limit={limit}"
    return requests.get(url, headers=headers).text

"""
---getnftdata---- >>>> given an nft (likely returned from getnftsfromcollection, returns a dictionary that contains the more useful data

id and collection for getting best listing
desc, image, and is_nsfw to match customer preferences
"""

# good to have
def getnftdata(nft):
    return {
        "identifier" : nft['identifier'],
        "collection" : nft['collection'],
        "name": nft['name'],
        "description": nft['description'],
        "image_url" : nft['image_url'],
        "is_nsfw" : nft['is_nsfw']
    }


# test collection
# "kai583264"
# nft id: 29, 30 (only ones with valid listings)

# # overall flow

# random for now just for sims
def agent(description, image_url, is_nsfw):
    return random.randint(1, 10)

col_nfts_map = {}

# collections = getcollections() # get collections 

collections = [{"collection": "kai583264"}] # cause collections still dosent work

collection_slugs = getslugsfromcollections(collections) # get collection ids
for slug in collection_slugs: # for each id
    col_nfts_map[slug] = getnftsfromcollection(slug, 3)


# find cllection with highest score
max_score = [None, float("-inf")] # [slug, score]

for slug, nfts in col_nfts_map.items():
    nftdata = getnftdata(nfts[0]) # first nft to try and narrow the search (this is assuming collection will be similar)
    score = agent(nftdata["description"], nftdata["image_url"], nftdata["is_nsfw"]) # use agent to score it
    if score > max_score[1]: # update highest scoring
        max_score = [slug, score]

# find NFT with highest score
max_score_nft = [None, float("-inf")]

for nft in col_nfts_map[max_score[0]]:
    nftdata = getnftdata(nft)

    # print it formated
    print(f"""
        identifier: {nftdata["identifier"]}
        collection: {nftdata["collection"]}
        name: {nftdata["name"]}
        description: {nftdata["description"]}
        image_url: {nftdata["image_url"]}
        is_nsfw: {nftdata["is_nsfw"]}
    """)

    score = agent(nftdata["description"], nftdata["image_url"], nftdata["is_nsfw"]) # use agent to score it
    if score > max_score_nft[1]:
        max_score_nft = [nft, score]

print(max_score_nft)



