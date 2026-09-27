class Monster:
    def __init__(self, base, level):
        self.id = base["card_detail_id"]
        self.name = base["name"]
        self.mana = base["mana"]
        self.level = level

        stats = base["stats"]
        idx = level - 1

        self.attack = stats["attack"][idx]
        self.magic = stats["magic"][idx]
        self.ranged = stats["ranged"][idx]
        self.armor = stats["armor"][idx]
        self.health = stats["health"][idx]
        self.speed = stats["speed"][idx]

        # cumulative abilities
        self.abilities = set()
        for i in range(level):
            self.abilities.update(base["abilities_by_level"][i])

    def summary(self):
        return (
            f"{self.name} (Lvl {self.level})\n"
            f"  ⚔ {self.attack} ✨ {self.magic} 🏹 {self.ranged} "
            f"🛡 {self.armor} ❤️ {self.health} ⚡ {self.speed}\n"
            f"  Abilities: {', '.join(sorted(self.abilities))}"
        )

