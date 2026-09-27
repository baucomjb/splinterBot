from typing import List
from splinterlands.api.cards import get_player_cards, get_card_details
from splinterlands.game.card import Card
from splinterlands.game.stats import Stats

def _stat_at_level(values, level):
    """
    Safely extract a stat value at a given level.
    Handles int, list, or missing values.
    """
    if values is None:
        return 0

    # Static stat (summoners, items, some legacy cards)
    if isinstance(values, int):
        return values

    # Per-level stat array
    if isinstance(values, list):
        if not values:
            return 0
        if len(values) >= level:
            return values[level - 1]
        return values[-1]

    # Unexpected type
    return 0


def _extract_abilities(detail, level):
    """
    Extract all abilities a card has at its current level.
    Returns accumulated abilities from level 1 up to the card's level.
    """
    stats = detail.get("stats", {})
    abilities_by_level = stats.get("abilities", [])
    if not abilities_by_level:
        return []
    
    # Accumulate all abilities from level 1 to current level
    accumulated = []
    for lvl in range(1, level + 1):
        if lvl <= len(abilities_by_level):
            level_abilities = abilities_by_level[lvl - 1] or []
            for ability in level_abilities:
                if ability not in accumulated:  # Avoid duplicates
                    accumulated.append(ability)
    
    return accumulated


def build_card_pool(username: str) -> List[Card]:
    """
    Build a playable card pool for the player.
    Filters out:
    - Cards on land (land_id set)
    - Cards for sale (market_id set)
    - Cards delegated to others (delegated_to set)
    - Cards rented out (rental_type set)
    
    For duplicate cards, keeps only the highest level version.
    """
    owned_cards = get_player_cards(username)
    details = get_card_details()

    details_map = {d["id"]: d for d in details}
    
    # First pass: filter playable cards and track highest level per card
    card_by_detail_id = {}
    
    for card in owned_cards:
        detail = details_map.get(card["card_detail_id"])
        if not detail:
            continue
        
        # Filter out unplayable cards
        if card.get("land_id"):  # On land
            continue
        if card.get("market_id"):  # For sale
            continue
        if card.get("delegated_to"):  # Delegated
            continue
        if card.get("rental_type"):  # Rented
            continue
        
        card_detail_id = card["card_detail_id"]
        level = card.get("level", 1)
        
        # Keep highest level of each card
        if card_detail_id not in card_by_detail_id:
            card_by_detail_id[card_detail_id] = (card, detail, level)
        else:
            # Replace if this is a higher level
            existing_level = card_by_detail_id[card_detail_id][2]
            if level > existing_level:
                card_by_detail_id[card_detail_id] = (card, detail, level)
    
    # Second pass: build Card objects from filtered collection
    pool: List[Card] = []
    
    for card, detail, level in card_by_detail_id.values():
        stats_data = detail.get("stats", {})

        stats = Stats(
            melee=_stat_at_level(stats_data.get("attack"), level),
            magic=_stat_at_level(stats_data.get("magic"), level),
            ranged=_stat_at_level(stats_data.get("ranged"), level),
            armor=_stat_at_level(stats_data.get("armor"), level),
            health=_stat_at_level(stats_data.get("health"), level),
            speed=_stat_at_level(stats_data.get("speed"), level),
            mana=_stat_at_level(stats_data.get("mana"), level),
        )

        abilities = _extract_abilities(detail, level)
        abilities_by_level = detail.get("stats", {}).get("abilities", [])

        pool.append(
            Card(
                uid=card["uid"],
                card_detail_id=card["card_detail_id"],
                name=detail.get("name"),
                card_type=detail.get("type"),
                color=detail.get("color"),
                rarity=detail.get("rarity"),
                level=level,
                edition=card.get("edition"),
                gold=card.get("gold", False),
                abilities=abilities,
                stats=stats,
                status={
                    "on_land": False,  # Already filtered
                    "for_sale": False,  # Already filtered
                    "delegated": False,  # Already filtered
                    "rented": False,  # Already filtered
                },
                abilities_by_level=abilities_by_level
            )
        )

    return pool

