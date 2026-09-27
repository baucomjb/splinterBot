#!/usr/bin/env python3
import json
import requests
from pathlib import Path

BASE_URL = "https://api2.splinterlands.com"
OUT_DIR = Path("data")
OUT_DIR.mkdir(exist_ok=True)

MONSTERS_FILE = OUT_DIR / "monsters.json"
SUMMONERS_FILE = OUT_DIR / "summoners.json"


def fetch(endpoint):
    url = f"{BASE_URL}/{endpoint}"
    print(f"Fetching {url}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def normalize_stats(stats):
    """
    Ensures all stat fields are lists (per level).
    """
    def to_list(value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    return {
        "attack": to_list(stats.get("attack")),
        "magic": to_list(stats.get("magic")),
        "ranged": to_list(stats.get("ranged")),
        "armor": to_list(stats.get("armor")),
        "health": to_list(stats.get("health")),
        "speed": to_list(stats.get("speed")),
    }


def normalize_abilities(abilities):
    """
    Splinterlands abilities already come per-level.
    Ensure each entry is a list.
    """
    normalized = []
    for level in abilities or []:
        if level is None:
            normalized.append([])
        elif isinstance(level, list):
            normalized.append(level)
        else:
            normalized.append([level])
    return normalized


def build_definitions():
    card_details = fetch("cards/get_details")

    monsters = []
    summoners = []

    for card in card_details:
        card_type = card.get("type")

        base = {
            "card_detail_id": card["id"],
            "name": card["name"],
            "splinter": card.get("color"),
            "rarity": card.get("rarity"),
            "edition": card.get("edition"),
            "mana": card.get("mana"),
        }

        # ─────────────────────────────
        # MONSTERS
        # ─────────────────────────────
        if card_type == "Monster":
            monster = {
                **base,
                "attack_type": card.get("attack_type"),
                "stats_by_level": normalize_stats(card.get("stats", {})),
                "abilities_by_level": normalize_abilities(card.get("abilities")),
                "tags": []
            }
            monsters.append(monster)

        # ─────────────────────────────
        # SUMMONERS
        # ─────────────────────────────
        elif card_type == "Summoner":
            buffs_by_level = []
            for lvl in card.get("stats", {}).get("buffs", []):
                buffs_by_level.append(lvl or {})

            summoner = {
                **base,
                "buffs_by_level": buffs_by_level,
                "allowed_splinters": card.get("secondary_colors") or [card.get("color")],
                "tags": []
            }
            summoners.append(summoner)

    return monsters, summoners


def main():
    monsters, summoners = build_definitions()

    with open(MONSTERS_FILE, "w") as f:
        json.dump(monsters, f, indent=2)

    with open(SUMMONERS_FILE, "w") as f:
        json.dump(summoners, f, indent=2)

    print(f"✅ Wrote {len(monsters)} monsters → {MONSTERS_FILE}")
    print(f"✅ Wrote {len(summoners)} summoners → {SUMMONERS_FILE}")


if __name__ == "__main__":
    main()

