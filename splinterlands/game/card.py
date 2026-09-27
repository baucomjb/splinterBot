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
        status: Dict,
        abilities_by_level: List[List[str]] = None
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
        self.abilities_by_level = abilities_by_level or []  # Store for level-based queries

    def get_abilities_at_level(self, level: int) -> List[str]:
        """
        Get accumulated abilities this card would have at a specific level.
        
        Args:
            level: The level to get abilities for (1-based)
        
        Returns:
            List of abilities at that level
        """
        if not self.abilities_by_level or level < 1:
            return []
        
        # Accumulate all abilities from level 1 up to the given level
        accumulated = []
        for lvl in range(1, min(level + 1, len(self.abilities_by_level) + 1)):
            ability_list = self.abilities_by_level[lvl - 1] or []
            for ability in ability_list:
                if ability not in accumulated:
                    accumulated.append(ability)
        
        return accumulated

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

