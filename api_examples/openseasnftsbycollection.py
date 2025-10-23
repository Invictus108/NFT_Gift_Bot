import requests

# replace "collection_slug" with the field in the collection json called "collection"
# EX: "collection" : "0-117-9dbd", collection_slug = "0-117-9dbd"
# some just don't have NFTs, so things like best-listing won't work
url = "https://api.opensea.io/api/v2/collection/collection_slug/nfts"

headers = {
    "accept": "application/json",
    "x-api-key": "API-KEY"
}

response = requests.get(url, headers=headers)

print(response.text)