import requests
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

OPENSEA_API_KEY = OPNSEA_KEY = os.getenv('OPNSEA_APIKEY')
SEAPORT_ADDRESS = Web3.to_checksum_address("0x00000000000001ad428e4906ae43d8f9852d0dd6")

# Minimal ERC721 ABI for transfer
ERC721_ABI = [{
    "constant": False,
    "inputs": [
        {"name": "from", "type": "address"},
        {"name": "to", "type": "address"},
        {"name": "tokenId", "type": "uint256"}
    ],
    "name": "safeTransferFrom",
    "outputs": [],
    "type": "function"
}]


def buy_nft(slug, token_id, buyer_public, buyer_private_key, recipient_public):
    """
    1. Find listing on OpenSea
    2. Get fulfillment data
    3. Buy NFT
    4. After purchase, send the NFT to `recipient_public`
    """

    # ---------- 1. Get listing ----------
    listing_url = f"https://api.opensea.io/api/v2/listings/collection/{slug}/nfts/{token_id}"
    listing_headers = {"x-api-key": OPENSEA_API_KEY}

    listing_resp = requests.get(listing_url, headers=listing_headers).json()

    if "listings" not in listing_resp or len(listing_resp["listings"]) == 0:
        raise Exception("No active listing found for this NFT")

    listing = listing_resp["listings"][0]
    order_hash = listing["order_hash"]

    # Get contract + id so we can transfer later
    contract_address = listing["protocol_data"]["parameters"]["offer"][0]["token"]
    token_id = int(listing["protocol_data"]["parameters"]["offer"][0]["identifierOrCriteria"])

    # ---------- 2. Get fulfillment data ----------
    fulfill_url = "https://api.opensea.io/api/v2/listings/fulfillment_data"
    fulfill_payload = {
        "order_hash": order_hash,
        "chain": "ethereum",
        "protocol_address": SEAPORT_ADDRESS,
        "side": "buy",
        "fulfiller": buyer_public
    }

    fulfill_headers = {
        "x-api-key": OPENSEA_API_KEY,
        "Content-Type": "application/json"
    }

    fulfill_resp = requests.post(
        fulfill_url,
        json=fulfill_payload,
        headers=fulfill_headers
    ).json()

    if "fulfillment_data" not in fulfill_resp:
        raise Exception("Fulfillment data not returned.")

    tx_data = fulfill_resp["fulfillment_data"]["transaction"]

    # ---------- 3. Build buy transaction ----------
    tx = {
        "from": buyer_public,
        "to": tx_data["to"],
        "value": int(tx_data["value"]),
        "data": tx_data["data"],
        "nonce": w3.eth.get_transaction_count(buyer_public),
        "gas": int(tx_data.get("gas", 350000)),
        "gasPrice": w3.eth.gas_price,
        "chainId": 1,
    }

    # Sign + send buy tx
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=buyer_private_key)
    buy_tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print("Buy TX Hash:", buy_tx_hash.hex())

    # ---------- 4. Wait for the NFT to arrive ----------
    receipt = w3.eth.wait_for_transaction_receipt(buy_tx_hash)
    print("NFT purchase confirmed.")

    # ---------- 5. Transfer NFT to recipient ----------
    contract = w3.eth.contract(address=contract_address, abi=ERC721_ABI)

    transfer_tx = contract.functions.safeTransferFrom(
        buyer_public,
        recipient_public,
        token_id
    ).build_transaction({
        "from": buyer_public,
        "nonce": w3.eth.get_transaction_count(buyer_public),
        "gas": 120000,
        "gasPrice": w3.eth.gas_price,
        "chainId": 1,
    })

    signed_transfer_tx = w3.eth.account.sign_transaction(transfer_tx, private_key=buyer_private_key)
    transfer_tx_hash = w3.eth.send_raw_transaction(signed_transfer_tx.raw_transaction)

    print("Transfer TX Hash:", transfer_tx_hash.hex())

    return {
        "purchase_tx": buy_tx_hash.hex(),
        "transfer_tx": transfer_tx_hash.hex()
    }
