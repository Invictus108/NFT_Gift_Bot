"""
app.py

Flask backend for "open lootbox" flow.

When a user opens a lootbox:
  - POST /api/open-lootbox with JSON:
      {
        "walletAddress": "...",
        "imageUrl": "https://..."   # OPTIONAL: image to use for NFT(s)
      }
  - Backend:
      1) looks up user by wallet (email + name),
      2) generates prizes (NFT metadata),
      3) (in real code) mints NFTs on-chain,
      4) sends ONE email via SendGrid with all the NFT info,
      5) returns the prizes to the frontend.

Requirements (pip):
  pip install flask sendgrid python-dotenv

Environment variables:
  SENDGRID_API_KEY         = your SendGrid API key
  SENDGRID_TEMPLATE_ID     = your dynamic template ID
  SENDGRID_FROM_EMAIL      = verified sender email in SendGrid (e.g. rewards@yourproject.xyz)
  COLLECTION_NAME          = (optional) e.g. "LootBox Season 1"
  MARKETPLACE_NAME         = (optional) e.g. "Magic Eden"
  CHAIN_NAME               = (optional) e.g. "Solana"
  LOOTBOX_GIF_URL          = (optional) GIF URL for box opening animation
"""

import os
import logging
from typing import List, Dict, Any, Optional

from flask import Flask, request, jsonify
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Optional: load from .env for local dev
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, we just skip
    pass


# ------------------------------------------------------------------------------
# Config
# ------------------------------------------------------------------------------

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDGRID_TEMPLATE_ID = os.environ.get("SENDGRID_TEMPLATE_ID")
SENDGRID_FROM_EMAIL = os.environ.get("SENDGRID_FROM_EMAIL", "rewards@yourproject.xyz")  # TODO: set to verified sender

COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "LootBox Season 1")
MARKETPLACE_NAME = os.environ.get("MARKETPLACE_NAME", "Magic Eden")
CHAIN_NAME = os.environ.get("CHAIN_NAME", "Solana")
LOOTBOX_GIF_URL = os.environ.get(
    "LOOTBOX_GIF_URL",
    "https://cdn.yoursite.com/lootbox-opening.gif"
)

if not SENDGRID_API_KEY:
    raise RuntimeError("SENDGRID_API_KEY is not set")
if not SENDGRID_TEMPLATE_ID:
    raise RuntimeError("SENDGRID_TEMPLATE_ID is not set")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------

def shorten_wallet_address(wallet_address: str) -> str:
    """Shorten a wallet address like 0x1234…abcd."""
    if len(wallet_address) <= 12:
        return wallet_address
    return f"{wallet_address[:6]}…{wallet_address[-4:]}"


def generate_prizes_for_user(
    wallet_address: str,
    nft_image_url_input: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Simulated function to generate prizes for a given wallet.

    Args:
        wallet_address: wallet that opened the lootbox
        nft_image_url_input: if provided, this URL will be used
                             as the image for all NFTs in this stub.

    In real code, this would:
      - use your rarity logic
      - talk to your on-chain minting logic
      - return final tokenIds + metadata
    """
    # If the caller provided an image URL, use it; otherwise fall back to defaults
    img1 = nft_image_url_input or "https://cdn.yoursite.com/nfts/dragon-42.png"
    img2 = nft_image_url_input or "https://cdn.yoursite.com/nfts/potion-109.png"

    # TODO: Replace with real logic / on-chain mint
    return [
        {
            "token_id": "123",
            "nft_name": "Mythic Dragon #42",
            "nft_tier": "Mythic",
            "nft_image_url": img1,
            "view_on_marketplace_url": "https://magiceden.io/item-details/dragon-42",
        },
        {
            "token_id": "124",
            "nft_name": "Silver Potion #109",
            "nft_tier": "Uncommon",
            "nft_image_url": img2,
            "view_on_marketplace_url": "https://magiceden.io/item-details/potion-109",
        },
    ]


def get_user_by_wallet(wallet_address: str) -> Dict[str, str]:
    """
    Simulated function to look up the user by wallet.
    In real code, you'd query your users table in your DB.

    Expected return format:
      {
        "email": "jack@example.com",
        "name": "Jack"
      }
    """
    # TODO: Replace with real DB lookup
    # For now, just return a dummy user.
    return {
        "email": "jack@example.com",
        "name": "Jack",
    }


def send_prize_email(
    to_email: str,
    name: str,
    wallet_address_short: str,
    prizes: List[Dict[str, Any]],
) -> None:
    """
    Sends ONE email via SendGrid listing all prizes from a lootbox opening.

    Expects SendGrid dynamic template with fields like:
      {{name}}
      {{wallet_address_short}}
      {{collection_name}}
      {{marketplace_name}}
      {{chain_name}}
      {{lootbox_gif_url}}
      {{#each prizes}}
        <h1>You unlocked: {{nft_name}}</h1>
        <p>Tier: {{nft_tier}}</p>
        <img src="{{nft_image_url}}" alt="{{nft_name}}" />
        <a href="{{view_on_marketplace_url}}">View on marketplace</a>
      {{/each}}
    """
    if not SENDGRID_API_KEY or not SENDGRID_TEMPLATE_ID:
        raise RuntimeError("SendGrid API key or template ID not configured")

    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=to_email,
    )

    dynamic_data = {
        "name": name,
        "wallet_address_short": wallet_address_short,
        "collection_name": COLLECTION_NAME,
        "marketplace_name": MARKETPLACE_NAME,
        "chain_name": CHAIN_NAME,
        "lootbox_gif_url": LOOTBOX_GIF_URL,
        "prizes": prizes,
    }

    message.template_id = SENDGRID_TEMPLATE_ID
    message.dynamic_template_data = dynamic_data

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info("SendGrid response status: %s", response.status_code)
    except Exception:
        logger.exception("Failed to send SendGrid email")
        raise


def open_lootbox(wallet_address: str, nft_image_url_input: Optional[str] = None) -> Dict[str, Any]:
    """
    Main function you call when the user clicks "Open lootbox".

    Steps:
      1) Look up user (email / name) from wallet
      2) Generate prizes (NFTs) for this opening
      3) (In real code) mint NFTs on-chain here
      4) Send ONE email with all prizes via SendGrid
      5) (Optional) store prizes to DB with email_sent flag
    """
    user = get_user_by_wallet(wallet_address)
    if not user:
        raise ValueError("Unknown wallet address")

    email = user.get("email")
    name = user.get("name") or "GM"

    # Generate prizes, optionally using the provided image URL
    prizes_raw = generate_prizes_for_user(wallet_address, nft_image_url_input=nft_image_url_input)

    wallet_address_short = shorten_wallet_address(wallet_address)

    prizes_for_email = [
        {
            "nft_name": p["nft_name"],
            "nft_tier": p["nft_tier"],
            "nft_image_url": p["nft_image_url"],
            "view_on_marketplace_url": p["view_on_marketplace_url"],
        }
        for p in prizes_raw
    ]

    # In real code: ensure NFTs are minted here, token_ids final

    # Send the email
    send_prize_email(
        to_email=email,
        name=name,
        wallet_address_short=wallet_address_short,
        prizes=prizes_for_email,
    )

    # TODO (optional): persist to DB with email_sent = True

    return {
        "email": email,
        "prizes": prizes_raw,
    }


# ------------------------------------------------------------------------------
# Flask app + route
# ------------------------------------------------------------------------------

app = Flask(__name__)


@app.route("/api/open-lootbox", methods=["POST"])
def api_open_lootbox():
    """
    POST /api/open-lootbox
    Body JSON:
      {
        "walletAddress": "0x123...",
        "imageUrl": "https://..."   # OPTIONAL
      }

    Response:
      {
        "success": true,
        "email": "jack@example.com",
        "prizes": [
          {
            "token_id": "...",
            "nft_name": "...",
            "nft_tier": "...",
            "nft_image_url": "...",
            "view_on_marketplace_url": "..."
          },
          ...
        ]
      }
    """
    try:
        data = request.get_json(force=True, silent=False)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    wallet_address = (data or {}).get("walletAddress")
    nft_image_url_input = (data or {}).get("imageUrl")  # NEW: optional image URL from client

    if not wallet_address:
        return jsonify({"error": "walletAddress is required"}), 400

    try:
        result = open_lootbox(wallet_address, nft_image_url_input=nft_image_url_input)
        return jsonify(
            {
                "success": True,
                "email": result["email"],
                "prizes": result["prizes"],
            }
        )
    except ValueError as ve:
        logger.warning("User error in open_lootbox: %s", ve)
        return jsonify({"error": str(ve)}), 400
    except Exception:
        logger.exception("Error opening lootbox")
        return jsonify({"error": "Failed to open lootbox"}), 500


if __name__ == "__main__":
    # For local dev; in production use gunicorn/uvicorn/etc.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
