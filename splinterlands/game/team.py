"""
Team module for managing battle team selection and submission
"""
from typing import List, Dict, Optional, Tuple
from splinterlands.game.card import Card
from splinterlands.api import client


class Team:
    """Represents a selected battle team"""
    
    def __init__(self, battle_id: str, summoner: Card, monsters: List[Card]):
        self.battle_id = battle_id
        self.summoner = summoner
        self.monsters = monsters
        self.splinter = self._determine_splinter()
    
    def _determine_splinter(self) -> str:
        """Determine the splinter based on summoner color"""
        color_to_splinter = {
            "Red": "Fire",
            "Blue": "Water",
            "Green": "Earth",
            "White": "Life",
            "Black": "Death",
            "Green/Red": "Dragon",  # For dragon cards
        }
        return color_to_splinter.get(self.summoner.color, "")
    
    def to_submission_dict(self) -> Dict:
        """Convert team to API submission format"""
        return {
            "battle_id": self.battle_id,
            "summoner_id": self.summoner.uid,
            "monsters": [m.uid for m in self.monsters],
            "splinter": self.splinter,
        }
    
    def summary(self) -> str:
        """Get formatted team summary"""
        lines = [f"\n=== Team Summary ==="]
        lines.append(f"Battle ID: {self.battle_id}")
        lines.append(f"Splinter: {self.splinter}")
        lines.append(f"Summoner: {self.summoner.name} (Lvl {self.summoner.level})")
        lines.append(f"Monsters ({len(self.monsters)})")
        for i, m in enumerate(self.monsters, 1):
            lines.append(f"  {i}. {m.name} (Lvl {m.level}) - {m.stats.summary()}")
        return "\n".join(lines)


class TeamManager:
    """Manages team selection and submission"""
    
    def __init__(self, username: str, posting_key: str):
        self.username = username
        self.posting_key = posting_key
    
    def create_team(
        self,
        battle_id: str,
        summoner: Card,
        monsters: List[Card]
    ) -> Team:
        """Create a team object from selected cards"""
        return Team(battle_id, summoner, monsters)
    
    def submit_team(self, team: Team) -> Dict:
        """
        Submit selected team to the API
        
        Args:
            team: Team object with summoner and monsters
        
        Returns:
            API response
        
        Raises:
            Exception: If submission fails
        """
        submission_data = team.to_submission_dict()
        
        try:
            response = client.submit_team(
                self.username,
                self.posting_key,
                submission_data
            )
            return response
        except Exception as e:
            raise Exception(f"Failed to submit team: {str(e)}")
    
    def submit_and_confirm(self, team: Team) -> bool:
        """
        Submit team and verify confirmation
        
        Returns:
            True if submission successful, False otherwise
        """
        try:
            print("\n📤 Submitting Team...")
            response = self.submit_team(team)
            
            if response.get("success"):
                print("✅ Team submitted successfully!")
                print(f"   Battle ID: {team.battle_id}")
                return True
            else:
                print(f"❌ Submission failed: {response.get('message', 'Unknown error')}")
                return False
        
        except Exception as e:
            print(f"❌ Submission error: {str(e)}")
            return False
