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
    stats = detail.get("stats", {})
    abilities_by_level = stats.get("abilities", [])
    if not abilities_by_level:
        return []
    if len(abilities_by_level) >= level:
        return abilities_by_level[level - 1] or []
    return abilities_by_level[-1] or []


def build_card_pool(username: str) -> List[Card]:
    owned_cards = get_player_cards(username)
    details = get_card_details()

    details_map = {d["id"]: d for d in details}
    pool: List[Card] = []

    for card in owned_cards:
        detail = details_map.get(card["card_detail_id"])
        if not detail:
            continue

        level = card.get("level", 1)
        stats_data = detail.get("stats", {})

        stats = Stats(
            melee=_stat_at_level(stats_data.get("attack"), level),
            magic=_stat_at_level(stats_data.get("magic"), level),
            ranged=_stat_at_level(stats_data.get("ranged"), level),
            armor=_stat_at_level(stats_data.get("armor"), level),
            health=_stat_at_level(stats_data.get("health"), level),
            speed=_stat_at_level(stats_data.get("speed"), level),
        )

        abilities = _extract_abilities(detail, level)

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
                    "on_land": bool(card.get("land_id")),
                    "for_sale": bool(card.get("market_id")),
                    "delegated": bool(card.get("delegated_to")),
                    "rented": bool(card.get("rental_type")),
                }
            )
        )

    return pool

