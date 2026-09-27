from splinterlands.api.fetch import fetch_cards

def load_card_index():
    cards = fetch_cards()
    return {c["card_detail_id"]: c for c in cards}

