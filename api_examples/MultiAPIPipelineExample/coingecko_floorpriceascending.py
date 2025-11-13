import os, requests
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('CGECKO_APIKEY')

#Inputs
per_page = 250 # Anything 1-250

url = "https://api.coingecko.com/api/v3/nfts/list"
headers = {"x-cg-demo-api-key": f"{API_KEY}",
           "per_page":f"{per_page}"} # 250 is the max I can get with one call
            # But there's also a page counter that lets you go multiple pages (consider later)
querystring = {"order":"floor_price_native_asc"}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())

# Returns a list of collections
# Important output: "contract_address"
"""
{
    "id": "ai-whisky",
    "contract_address": "0xa2a8fbbacd45528ffec45ced448a9e2a9c3cfcff",
    "name": "Ai Whisky",
    "asset_platform_id": "avalanche",   ----Blockhain basically (ones we want will have "ethereum")
    "symbol": "AIWHISKY"
},
"""