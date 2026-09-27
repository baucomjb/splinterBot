"""
Summoner abilities loader - retrieves summoner team buffs/debuffs.
"""

import yaml
import os
from typing import Dict, List, Optional


class SummonerAbilities:
    """Loads and retrieves summoner team abilities"""
    
    _instance = None
    _abilities = None
    
    def __new__(cls):
        """Singleton pattern to load abilities only once"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_abilities()
        return cls._instance
    
    def _load_abilities(self):
        """Load summoner abilities from YAML file"""
        # Try multiple possible locations for the YAML file
        possible_paths = [
            os.path.join(
                os.path.dirname(__file__),
                "../../data/summoner_abilities.yaml"
            ),
            os.path.join(
                os.path.dirname(__file__),
                "../data/summoner_abilities.yaml"
            ),
            os.path.join(
                os.getcwd(),
                "data/summoner_abilities.yaml"
            ),
            "/home/jbaucom/code/splinterlands_bot/data/summoner_abilities.yaml"
        ]
        
        abilities_file = None
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                abilities_file = abs_path
                break
        
        if abilities_file is None:
            print(f"Warning: summoner_abilities.yaml not found. Summoner abilities disabled.")
            self._abilities = {}
            return
        
        try:
            with open(abilities_file, 'r') as f:
                self._abilities = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Error loading {abilities_file}: {e}")
            self._abilities = {}
    
    def get_summoner_abilities(self, summoner_name: str) -> Optional[List[str]]:
        """
        Get team abilities for a summoner.
        
        Args:
            summoner_name: Name of the summoner (e.g., "Kelya Frendul")
        
        Returns:
            List of ability descriptions, or None if not found
        """
        if not self._abilities:
            return None
        
        # Search through all card sets for the summoner
        for card_set, summoners in self._abilities.items():
            if isinstance(summoners, dict) and summoner_name in summoners:
                summoner_data = summoners[summoner_name]
                # Support both "abilities" and "team_buffs" field names
                return summoner_data.get("team_buffs") or summoner_data.get("abilities")
        
        return None

    def get_summoner_pallando_options(self, summoner_name: str) -> Optional[list]:
        """
        Get Pallando options (special unit ability selections) for a summoner.
        
        Args:
            summoner_name: Name of the summoner (e.g., "Elias Max Pruitt")
        
        Returns:
            List of pallando option dicts, or None if not found
        """
        if not self._abilities:
            return None
        
        # Search through all card sets for the summoner
        for card_set, summoners in self._abilities.items():
            if isinstance(summoners, dict) and summoner_name in summoners:
                summoner_data = summoners[summoner_name]
                return summoner_data.get("pallando_options")
        
        return None


# Global instance
_abilities_instance = None


def get_summoner_abilities_loader() -> SummonerAbilities:
    """Get the global SummonerAbilities instance"""
    global _abilities_instance
    if _abilities_instance is None:
        _abilities_instance = SummonerAbilities()
    return _abilities_instance
