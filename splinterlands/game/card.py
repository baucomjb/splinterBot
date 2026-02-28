from typing import List, Dict
from splinterlands.game.stats import Stats


class Card:
    def __init__(
        self,
        uid: str,
        card_detail_id: int,
        name: str,
        card_type: str,
        color: str,
        rarity: int,
        level: int,
        edition: int,
        gold: bool,
        abilities: List[str],
        stats: Stats,
        status: Dict
    ):
        self.uid = uid
        self.card_detail_id = card_detail_id
        self.name = name
        self.type = card_type
        self.color = color
        self.rarity = rarity
        self.level = level
        self.edition = edition
        self.gold = gold
        self.abilities = abilities
        self.stats = stats
        self.status = status

    def summary(self) -> str:
        flags = []
        for k, v in self.status.items():
            if v:
                flags.append(k.replace("_", " ").title())

        flag_str = f" [{' | '.join(flags)}]" if flags else ""
        abilities = ", ".join(self.abilities) if self.abilities else "None"

        return (
            f"{self.name} (Lvl {self.level}){flag_str}\n"
            f"  {self.stats.summary()}\n"
            f"  Abilities: {abilities}"
        )

