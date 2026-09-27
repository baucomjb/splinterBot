import requests
import json
from pathlib import Path

BASE = "https://api2.splinterlands.com"

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def fetch_cards():
    path = DATA_DIR / "cards.json"
    if path.exists():
        return json.load(open(path))

    cards = requests.get(f"{BASE}/cards/get_details").json()
    json.dump(cards, open(path, "w"), indent=2)
    return cards


def fetch_player_cards(username):
    path = DATA_DIR / "player_cards.json"
    cards = requests.get(f"{BASE}/cards/collection/{username}").json()
    json.dump(cards, open(path, "w"), indent=2)
    return cards

