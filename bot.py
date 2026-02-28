import yaml
from splinterlands.game.card_pool import build_card_pool


def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    username = config["account"]["username"]

    print(f"Loading card pool for {username}...\n")

    cards = build_card_pool(username)

    print(f"Total cards found: {len(cards)}\n")

    # Print first 10 cards
    for card in cards[:10]:
        print(card.summary())


if __name__ == "__main__":
    main()

