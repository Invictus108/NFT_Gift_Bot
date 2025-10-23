import requests

url = "https://deep-index.moralis.io/api/v2.2/nft/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/floor-price?chain=eth"

headers = {
  "Accept": "application/json",
  "X-API-Key": "YOUR_API_KEY"
}

response = requests.request("GET", url, headers=headers)

print(response.text)