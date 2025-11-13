import os, requests
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('ALCHEM_APIKEY')

#Inputs
contract_address = "0xd07dc4262bcdbf85190c01c996b4c06a461d2430" # Example

url = f"https://eth-mainnet.g.alchemy.com/nft/v3/{API_KEY}/getFloorPrice"
querystring = {"contractAddress":contract_address}

response = requests.get(url, params=querystring)

print(response.json())

# Straightforward - Give it a contract and it will give you FLOOR PRICE on multiple marketplaces
# Important output: "floorPrice", available MarketPlaces, "collectionURL" for getting collection_slug in OpenSeas

"""
{
   "openSea":{
      "floorPrice":1e-14,
      "priceCurrency":"ETH",
      "collectionUrl":"https://opensea.io/collection/rarible", --> 'rarible' is the collection_slug
      "retrievedAt":"2025-11-13T03:50:00.749Z",
      "error":"None"
   },
   "looksRare":{
      "floorPrice":0.00245,
      "priceCurrency":"ETH",
      "collectionUrl":"https://looksrare.org/collections/0xd07dc4262bcdbf85190c01c996b4c06a461d2430",
      "retrievedAt":"2025-02-13T12:05:45.729Z",
      "error":"None"
   }
}
"""