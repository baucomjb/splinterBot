class BattleState:
    def __init__(self, raw_player_data: dict):
        self.raw = raw_player_data
        self.battle = raw_player_data.get("battle")

        if not self.battle:
            raise ValueError("No active battle found")

        self.battle_id = self.battle.get("id")
        self.mana_cap = int(self.battle.get("mana_cap", 0))
        self.rulesets = self._parse_rulesets()
        self.allowed_splinters = self._parse_splinters()
        self.opponent = self.battle.get("opponent")

    def _parse_rulesets(self):
        rules = self.battle.get("ruleset", "")
        return [r.strip() for r in rules.split("|") if r]

    def _parse_splinters(self):
        inactive = self.battle.get("inactive", "")
        all_splinters = {"Fire", "Water", "Earth", "Life", "Death", "Dragon"}
        inactive_set = set(i.strip() for i in inactive.split(",") if i)
        return list(all_splinters - inactive_set)

    def summary(self):
        return {
            "battle_id": self.battle_id,
            "mana": self.mana_cap,
            "rulesets": self.rulesets,
            "splinters": self.allowed_splinters,
            "opponent": self.opponent,
        }

