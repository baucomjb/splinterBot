"""
Account module for managing player account data
"""
from typing import Dict, Optional
from splinterlands.api import client


class Account:
    """Represents a player account with profile and battle data"""
    
    def __init__(self, username: str):
        self.username = username
        self.profile = None
        self.battle_data = None
        
    def download(self) -> Dict:
        """
        Download all account data from API
        
        Returns:
            Dict with keys: profile, battle_data
        """
        # Get account profile and stats
        self.profile = client.get_player_account(self.username)
        
        # Get current battle status
        self.battle_data = client.get_current_battle(self.username)
        
        return {
            "profile": self.profile,
            "battle_data": self.battle_data
        }
    
    def get_rating(self) -> int:
        """Get current rating"""
        if not self.profile:
            return 0
        return int(self.profile.get("rating", 0))
    
    def get_wins(self) -> int:
        """Get total wins"""
        if not self.profile:
            return 0
        return int(self.profile.get("wins", 0))
    
    def get_battles(self) -> int:
        """Get total battles"""
        if not self.profile:
            return 0
        return int(self.profile.get("battles", 0))
    
    def get_win_rate(self) -> float:
        """Get win percentage"""
        battles = self.get_battles()
        if battles == 0:
            return 0.0
        return (self.get_wins() / battles) * 100
    
    def get_season_info(self) -> Dict:
        """Get current season information"""
        if not self.profile:
            return {}
        return {
            "rating": self.get_rating(),
            "wins": self.get_wins(),
            "battles": self.get_battles(),
            "win_rate": round(self.get_win_rate(), 1),
            "league": self.profile.get("league", "Unknown"),
            "collection_power": self.profile.get("collection_power", 0),
        }
    
    def has_active_battle(self) -> bool:
        """Check if player has an active battle"""
        if not self.battle_data:
            return False
        
        # Check for "battle" field (primary indicator)
        has_battle = bool(self.battle_data.get("battle"))
        
        # Debug: log what we're checking
        import logging
        logger = logging.getLogger(__name__)
        if not has_battle:
            # Log the actual structure so we can see what's there
            logger.debug(f"No 'battle' field in response. Keys: {list(self.battle_data.keys())[:10]}")
        
        return has_battle
    
    def has_wild_pass(self) -> bool:
        """Check if player owns a Wild Pass for current season"""
        if not self.profile:
            return False
        # The API returns pass ownership info in the profile
        # Common field names: wild_pass, summoner_pass, summoner_pass_active, etc.
        wild_pass = self.profile.get("wild_pass", False)
        summoner_pass = self.profile.get("summoner_pass", False)
        return bool(wild_pass or summoner_pass)
    
    def get_pass_info(self) -> str:
        """Get pass ownership status"""
        if not self.profile:
            return "Pass info: Unknown"
        wild_pass = self.profile.get("wild_pass", False)
        summoner_pass = self.profile.get("summoner_pass", False)
        
        passes = []
        if wild_pass:
            passes.append("Wild Pass")
        if summoner_pass:
            passes.append("Summoner Pass")
        
        if passes:
            return f"Passes: {', '.join(passes)}"
        else:
            return "Passes: None owned"
    
    def summary(self) -> str:
        """Return a formatted summary of account data"""
        lines = [f"\n=== Account Summary for {self.username} ==="]
        
        if self.profile:
            lines.append(f"Rating: {self.get_rating()}")
            lines.append(f"Record: {self.get_wins()}W - {self.get_battles() - self.get_wins()}L ({self.get_win_rate():.1f}%)")
            lines.append(f"Collection Power: {self.profile.get('collection_power', 'N/A')}")
            league = self.profile.get("league", "N/A")
            lines.append(f"League: {league}")
            lines.append(self.get_pass_info())
        
        if self.battle_data:
            if self.has_active_battle():
                lines.append("Status: BATTLE ACTIVE ⚔️")
            else:
                lines.append("Status: Idle (waiting for battle)")
        
        return "\n".join(lines)

