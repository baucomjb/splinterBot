# splinterlands/game/stats.py

class Stats:
    def __init__(
        self,
        melee: int = 0,
        magic: int = 0,
        ranged: int = 0,
        armor: int = 0,
        health: int = 0,
        speed: int = 0,
        mana: int = 0,
    ):
        self.melee = melee
        self.magic = magic
        self.ranged = ranged
        self.armor = armor
        self.health = health
        self.speed = speed
        self.mana = mana

    def summary(self) -> str:
        return (
            f"⚔ M:{self.melee} "
            f"✨:{self.magic} "
            f"🏹:{self.ranged} "
            f"🛡:{self.armor} "
            f"❤️:{self.health} "
            f"⚡:{self.speed} "
            f"💎:{self.mana}"
        )


