import os, requests
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('OPNSEA_APIKEY')

#Inputs
collection_slug = "rarible" # Example slug

url = f"https://api.opensea.io/api/v2/listings/collection/{collection_slug}/all"
headers = {"accept": "*/*",
           "x-api-key": f"{API_KEY}",}

response = requests.get(url, headers=headers)

print(response.text)

# Given Collection_slug, gives listings

""" GUIDE: WHAT YOU'RE ACTUALLY LOOKING FOR
>Each listing contains...
- "price" > "current" -- IMPORTANT FOR PRICE
    >In "current"
    - "currency"
    - "decimals"
    - "value"
    >Calculate price which is value / (10^decimals)
- "protocol_data" > "parameters" > "offer" -- 
    >In "offer"
    - "token"
    - "identifierOrCriteria"
"""
# EXAMPLE LISTING
"""
{
 "order_hash":"0x80be6333914d3db5da562e126561732a74477f6365e9928bbd2244dc529fb812",
 "chain":"ethereum",
 "protocol_data":{
    "parameters":{
       "offerer":"0xe27a2af1eac7ea9fd088d6ffd0aadcf00990a7ee",
       "offer":[
          {
             "itemType":3,
             "token":"0xb66a603f4cfe17e3d27b87a8bfcad319856518b8",
             "identifierOrCriteria":"102438555517140195776407581303565463466153928031174529427366276826787968188458",
             "startAmount":"1",
             "endAmount":"1"
          }
       ],
       "consideration":[
          {
             "itemType":0,
             "token":"0x0000000000000000000000000000000000000000",
             "identifierOrCriteria":"0",
             "startAmount":"8900",
             "endAmount":"8900",
             "recipient":"0xe27a2af1eac7ea9fd088d6ffd0aadcf00990a7ee"
          },
          {
             "itemType":0,
             "token":"0x0000000000000000000000000000000000000000",
             "identifierOrCriteria":"0",
             "startAmount":"100",
             "endAmount":"100",
             "recipient":"0x0000a26b00c1f0df003000390027140000faa719"
          },
          {
             "itemType":0,
             "token":"0x0000000000000000000000000000000000000000",
             "identifierOrCriteria":"0",
             "startAmount":"1000",
             "endAmount":"1000",
             "recipient":"0xdf13c577749c79c2078d4f040ccb75513267edfb"
          }
       ],
       "startTime":"1758053996",
       "endTime":"1773605996",
       "orderType":0,
       "zone":"0x0000000000000000000000000000000000000000",
       "zoneHash":"0x0000000000000000000000000000000000000000000000000000000000000000",
       "salt":"0x3d958fe20000000000000000000000000000000000000000f06baea9b115e3b7",
       "conduitKey":"0x0000007b02230091a7ed01230072f7006a004d60a8d4e71d599b8104250f0000",
       "totalOriginalConsiderationItems":3,
       "counter":0
    },
    "signature":null
 },
 "protocol_address":"0x0000000000000068f116a894984e2db1123eb395",
 "remaining_quantity":1,
 "price":{
    "current":{
       "currency":"ETH",
       "decimals":18,
       "value":"10000"
    }
 },
 "type":"basic",
 "status":"ACTIVE"
},
"""