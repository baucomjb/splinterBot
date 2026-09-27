class Summoner:
    def __init__(self, base):
        self.id = base["card_detail_id"]
        self.name = base["name"]
        self.splinter = base["splinter"]
        self.effects = base["summoner_effects"]

    def summary(self):
        buffs = self.effects["stat_buffs"]
        return f"{self.name} | Buffs: {buffs}"

