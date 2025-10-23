import requests

url = "https://api.opensea.io/api/v2/collections?"
headers = {
    "accept": "application/json",
    "x-api-key": "bb7a25e2f18e46cabc97a8090de9b1da"
}

# first 100 collections, unsorted
response = requests.get(url, headers=headers)

if __name__ == '__main__':
    print(response.text)

"""
Notable Query Params

https://docs.opensea.io/reference/list_collections

chain= 
- Lets you sort by blockchain
- NOTE: Broken as hell!!!! If u use it without also using the query param "order_by" you get an internal server error.
also it specifically hates when you use order_by=created_date

next=
- Each collections query returns a json. the final field in that json is a sequence of chars called "next"
- If you put that sequence into the next= param of a new query you'll effectively go to the "next page"
- i.e. next 50 or 100 or 200 collections under the same criteria

order_by=
- created_date doesn't seem to work. always returns "Internal Server Error"
- the rest seem to work though. orders the responses by a specific

Example Collection

{
    "collection" : "0-117-9dbd",
    "name" : "#0 117 9dbd",
    "description" : "",
    "image_url" : "https://i2.seadn.io/base/0x3cb94d4df89ba31812abab1463a25875ee9181df/7180f9bd3ba9fc5533676c37b8f6b0/cf7180f9bd3ba9fc5533676c37b8f6b0.jpeg",
    "banner_image_url" : "",
    "owner" : "0x3fcb734a24b47a8d1ef73271a5390f06f9b68460",
    "safelist_status" : "not_requested",
    "category" : "",
    "is_disabled" : false,
    "is_nsfw" : false,
    "trait_offers_enabled" : false,
    "collection_offers_enabled" : true,
    "opensea_url" : "https://opensea.io/collection/0-117-9dbd",
    "project_url" : "",
    "wiki_url" : "",
    "discord_url" : "",
    "telegram_url" : "",
    "twitter_username" : null,
    "instagram_username" : "",
    "contracts" : [ {
      "address" : "0x3cb94d4df89ba31812abab1463a25875ee9181df",
      "chain" : "base"
    } ]
  }

"""
