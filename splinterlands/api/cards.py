# splinterlands/api/cards.py

import requests
import json
from typing import List, Dict

BASE_URL = "https://api2.splinterlands.com"


def get_player_cards(username: str) -> List[Dict]:
    """
    Returns a normalized list of card objects owned by a player.
    Handles inconsistent API behavior where 'cards' may be a list or JSON string.
    """
    url = f"{BASE_URL}/cards/collection/{username}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()

    data = resp.json()
    cards = data.get("cards", [])

    # API inconsistency handling
    if isinstance(cards, str):
        cards = json.loads(cards)

    if not isinstance(cards, list):
        raise RuntimeError(f"Unexpected cards payload type: {type(cards)}")

    return cards


def get_card_details() -> List[Dict]:
    """
    Returns static card metadata (abilities, stats, rarity)
    """
    url = f"{BASE_URL}/cards/get_details"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()

