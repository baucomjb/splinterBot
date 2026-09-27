from splinterlands.api.fetch import fetch_player_cards
from splinterlands.data.loader import load_card_index
from splinterlands.game.monster import Monster
from splinterlands.game.summoner import Summoner

def build_card_pool(username):
    index = load_card_index()
    owned = fetch_player_cards(username)

    monsters = []
    summoners = []

    for card in owned:
        base = index.get(card["card_detail_id"])
        if not base:
            continue

        level = card["level"]

        if base.get("type") == "Summoner":
            summoners.append(Summoner(base))
        else:
            monsters.append(Monster(base, level))

    return { "monsters": monsters,
            "summoners": summoners
            }

