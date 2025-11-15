import requests
import os
from dotenv import load_dotenv

load_dotenv()
CGECKO_KEY = os.getenv('CGECKO_APIKEY')
ALCCHEM_KEY = os.getenv('ALCHEM_APIKEY')
OPNSEA_KEY = os.getenv('OPNSEA_APIKEY')

# ['0xd07dc4262bcdbf85190c01c996b4c06a461d2430', '0x90cA8a3eb2574F937F514749ce619fDCCa187d45', '0xa342f5d851e866e18ff98f351f2c6637f4478db5', '0x76BE3b62873462d2142405439777e971754E8E77', '0x57f1887a8bf19b14fc0df6fd9b2acc9af147ea85', '0x1eb7382976077f92cf25c27cc3b900a274fd0012', '0x8fb956ce2921954c45cb3bb41978c4c6c9736af2', '0x0baeccd651cf4692a8790bcc4f606e79bf7a3b1c']

def getCollectionsAscPriceFloor(num=250, blockchain="ethereum"):
    url = "https://api.coingecko.com/api/v3/nfts/list"
    headers = {"x-cg-demo-api-key": f"{CGECKO_KEY}",
               "per_page": f"{num}"}
    querystring = {"order": "floor_price_native_asc"}

    response = requests.get(url, headers=headers, params=querystring).json()
    results = [obj for obj in response if obj.get("asset_platform_id") == blockchain]
    return [r.get("contract_address") for r in results]

def getMarketplaceCollectionAddress(contract_address, marketplace="openSea"):
    url = f"https://eth-mainnet.g.alchemy.com/nft/v3/{ALCCHEM_KEY}/getFloorPrice"
    querystring = {"contractAddress":contract_address}

    response = requests.get(url, params=querystring).json()

    if marketplace in response:
        if marketplace == "openSea":
            collect_url = response[marketplace].get("collectionUrl")
            return collect_url.rstrip("/").split("/")[-1]
        else:
            return response[marketplace].get("collectionUrl")
    else:
        return []  # empty list if marketplace key not found

def getAllListings(collection_slug, price_celing):
    url = f"https://api.opensea.io/api/v2/listings/collection/{collection_slug}/all"
    headers = {"accept": "*/*",
               "x-api-key": f"{OPNSEA_KEY}", }

    response = requests.get(url, headers=headers).json()
    orders = response.get("listings", [])

    results = []

    for order in orders:
        # Only keep ACTIVE listings
        if order.get("status") != "ACTIVE":
            continue
        # --- Extract from price.current ---
        price_info = order.get("price", {}).get("current", {})
        currency = price_info.get("currency")
        decimals = int(price_info.get("decimals"))
        value = float(price_info.get("value"))
        price = value / (10 ** decimals)

        # --- Extract from protocol_data.parameters.offer[0] ---
        params = order.get("protocol_data", {}).get("parameters", {})
        offer_list = params.get("offer", [])
        token = None
        identifier = None

        if offer_list:
            offer = offer_list[0]
            token = offer.get("token")
            identifier = offer.get("identifierOrCriteria")

        # Build a minimal object with only what you want
        results.append({
            "currency": currency,
            "price": price,
            "token": token,
            "identifierOrCriteria": identifier
        })

    return [r for r in results if r.get("price") is not None and r["price"] <= price_celing]

def getNFT(address, identifier):
    url = f"https://api.opensea.io/api/v2/chain/ethereum/contract/{address}/nfts/{identifier}"
    headers = {"accept": "*/*",
               "x-api-key": f"{OPNSEA_KEY}", }

    response = requests.get(url, headers=headers).json()

    nft = response.get("nft", {})
    results = {
        "name": nft.get("name"),
        "description": nft.get("description"),
        "image_url": nft.get("image_url")
    }
    return results

def getNftWithPriceCeling(price_celing):
    ascCollect = getCollectionsAscPriceFloor()
    collectSlugs = []
    for c in ascCollect:
        collectSlugs.append(getMarketplaceCollectionAddress(c))
    listings = []
    for l in collectSlugs:
        listings.extend(getAllListings(l, price_celing))
    nfts = []
    for ls in listings:
        nfts.append(getNFT(ls.get("token"), ls.get("identifierOrCriteria")).update({"currency":ls.get("currency"),"price":ls.get("price")}))
    return nfts

if __name__ == '__main__':
    print(getNftWithPriceCeling(999)) # takes so long I have no idea if it works