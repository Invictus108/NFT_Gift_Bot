import requests

# same as get nfts by collection -> replace collection_slug with collection identifier
# will return [] if there's no listings.
# can't seem to find a filter to find collections with listings, but you can also get listings by individual blockchain
url = "https://api.opensea.io/api/v2/listings/collection/collection_slug/best"
# example of active collection with listings collection_slug:"hypurr-hyperevm"

headers = {
    "accept": "application/json",
    "x-api-key": "API-KEY"
}

response = requests.get(url, headers=headers)

print(response.text)