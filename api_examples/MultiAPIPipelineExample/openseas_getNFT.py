import os, requests
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('OPNSEA_APIKEY')

# Inputs
address = "0xb66a603f4cfe17e3d27b87a8bfcad319856518b8" # Example -> is called "token" in the listing
identifier = "102438555517140195776407581303565463466153928031174529427366276826787968188458" # Example -> is called "identifierOrCriteria" in the listing

url = f"https://api.opensea.io/api/v2/chain/ethereum/contract/{address}/nfts/{identifier}"
headers = {"accept": "*/*",
           "x-api-key": f"{API_KEY}",}

response = requests.get(url, headers=headers)

print(response.text)

# Given address and identifier, gives NFT
# Important outputs include: "name", "description", "image_url", "is_nsfw"

"""
{
  "nft" : {
    "identifier" : "102438555517140195776407581303565463466153928031174529427366276826787968188458",
    "collection" : "rarible",
    "contract" : "0xb66a603f4cfe17e3d27b87a8bfcad319856518b8",
    "token_standard" : "erc1155",
    "name" : "Mine Bitcoin Today! ⛏️",
    "description" : "Mine Bitcoin \n\nFollow the link and get your FREE Bonus Miner Today!\n\nhttps://gomining.com/?ref=H_5su\n\nReferral code: H_5su\n\n1 TH/s Rigs starting at only $23.99 USD… Come Build with us!\n\nAlso Download the “Bitcoin Mining” app now and earn free BTC with me! My invitation code: KYRKLH\nApp store: https://apps.apple.com/us/app/id6503180820\nGoogle Play: https://play.google.com/store/apps/details?id=bitcoin.minning.com",
    "image_url" : "https://i2c.seadn.io/ethereum/0xb66a603f4cfe17e3d27b87a8bfcad319856518b8/2a704ca962125dd615830fdacdf20f/5c2a704ca962125dd615830fdacdf20f.jpeg",
    "display_image_url" : "https://i2c.seadn.io/ethereum/0xb66a603f4cfe17e3d27b87a8bfcad319856518b8/2a704ca962125dd615830fdacdf20f/5c2a704ca962125dd615830fdacdf20f.jpeg",
    "display_animation_url" : null,
    "metadata_url" : "ipfs://ipfs/bafkreihnlb23dehjwfvziukxcphnoo2rydtzrfipp57g7oj56megnxqpx4",
    "opensea_url" : "https://opensea.io/assets/ethereum/0xb66a603f4cfe17e3d27b87a8bfcad319856518b8/102438555517140195776407581303565463466153928031174529427366276826787968188458",
    "updated_at" : "2025-11-13T06:09:34.898689",
    "is_disabled" : false,
    "is_nsfw" : false,
    "animation_url" : null,
    "is_suspicious" : false,
    "creator" : "",
    "traits" : [ ],
    "owners" : [ ],
    "rarity" : null
  }
}
"""