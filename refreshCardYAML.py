import requests
import yaml
import os
from collections import defaultdict

# --------------------------
# CONFIG
# --------------------------
USERNAME = "tardigrade123"  # replace with your username
BASE_URL = "https://api.splinterlands.io"
OUTPUT_DIR = "data/processed"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------
# FETCH DATA
# --------------------------

def fetch_collection():
    print("Fetching collection...")
    url = f"{BASE_URL}/cards/collection/{USERNAME}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    cards = data.get("cards", [])
    print(f"Total cards in collection: {len(cards)}")
    return cards

def fetch_card_details():
    print("Fetching card metadata...")
    url = f"{BASE_URL}/cards/get_details"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# --------------------------
# FILTERING
# --------------------------

def filter_usable(cards):
    usable = []
    for c in cards:
        reasons = []
        if c.get("delegated_to"):
            reasons.append("delegated")
        if c.get("stake_plot"):
            reasons.append("staked_on_land")
        if c.get("lock_days"):
            reasons.append("locked")
        # allow gold cards even if no normal foil exists
        usable.append(c)
    print(f"Usable cards after filtering: {len(usable)}")
    return usable

# --------------------------
# GROUP HIGHEST LEVEL
# --------------------------

def group_highest(cards):
    """
    Group by (card_detail_id, gold) so that gold and regular foil are separate
    """
    grouped = {}
    for c in cards:
        key = (c["card_detail_id"], c["gold"])
        if key not in grouped:
            grouped[key] = {
                "level": c["level"],
                "copies": 1,
                "gold": c["gold"],
            }
        else:
            grouped[key]["copies"] += 1
            if c["level"] > grouped[key]["level"]:
                grouped[key]["level"] = c["level"]
    print(f"Unique playable cards (including gold distinction): {len(grouped)}")
    return grouped

# --------------------------
# STAT + ABILITY EXTRACTION
# --------------------------

def extract_stat_array(stat_array):
    if stat_array is None:
        return [0]*8
    if isinstance(stat_array, list):
        return stat_array
    else:
        return [stat_array]*8

def extract_stats(detail):
    stats = detail.get("stats", {})
    output = {}
    for key in ["mana", "attack", "magic", "ranged", "speed", "armor", "health"]:
        output[key] = extract_stat_array(stats.get(key))
    return output

def extract_abilities(detail):
    """
    Return abilities as a list of lists per level.
    Handles dicts with "ability", strings, or missing.
    Ensures 8 levels.
    """
    raw = detail.get("abilities") or detail.get("abilities_data") or detail.get("stats", {}).get("abilities") or []
    abilities_by_level = []
    for lvl in range(8):
        lvl_data = raw[lvl] if lvl < len(raw) and raw[lvl] else []
        flat = []
        for a in lvl_data:
            if isinstance(a, dict) and "ability" in a:
                flat.append(a["ability"])
            elif isinstance(a, str):
                flat.append(a)
        abilities_by_level.append(flat)
    return abilities_by_level

# --------------------------
# BUILD SPLINTER YAML
# --------------------------

def build_yaml(grouped, details):
    detail_lookup = {d["id"]: d for d in details}
    splinters = defaultdict(lambda: {"summoners": [], "monsters": []})
    skipped = 0

    for (cid, is_gold), data in grouped.items():
        detail = detail_lookup.get(cid)
        if not detail:
            skipped += 1
            continue
        if detail.get("type") not in ["Monster", "Summoner"]:
            skipped += 1
            continue

        # Determine splinter
        color = detail.get("color", "neutral").lower()
        if color != "gold":
            splinter = color
        else:
            # gold card: use base splinter if present
            splinter = detail.get("splinter") or "neutral"

        card_type = "summoners" if detail["type"] == "Summoner" else "monsters"

        entry = {
            "name": detail["name"],
            "level": data["level"],
            "copies": data["copies"],
            "rarity": detail.get("rarity"),
            "gold": data["gold"],
            "abilities": extract_abilities(detail),
        }

        entry.update(extract_stats(detail))
        splinters[splinter][card_type].append(entry)

    print(f"Skipped {skipped} cards due to being non-playable or missing stats")
    return splinters

# --------------------------
# WRITE FILES
# --------------------------

def write_files(splinters):
    print("Writing YAML files...")
    for splinter, data in splinters.items():
        path = os.path.join(OUTPUT_DIR, f"{splinter}.yaml")
        with open(path, "w") as f:
            yaml.dump(
                {
                    "splinter": splinter,
                    "summoners": data["summoners"],
                    "monsters": data["monsters"],
                },
                f,
                sort_keys=False,
            )
        print(
            f"  Wrote {splinter}.yaml - {len(data['summoners'])} summoners, {len(data['monsters'])} monsters"
        )
    print("Done.")

# --------------------------
# MAIN
# --------------------------

def main():
    cards = fetch_collection()
    usable = filter_usable(cards)
    grouped = group_highest(usable)
    details = fetch_card_details()
    splinters = build_yaml(grouped, details)
    write_files(splinters)

if __name__ == "__main__":
    main()

