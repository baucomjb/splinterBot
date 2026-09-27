"""
Summoner constraints loader - retrieves max monster levels by rarity & summoner level.
"""

import yaml
import os
from typing import Dict, Optional


class SummonerConstraints:
    """Loads and validates summoner summoning constraints"""
    
    _instance = None
    _constraints = None
    
    def __new__(cls):
        """Singleton pattern to load constraints only once"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_constraints()
        return cls._instance
    
    def _load_constraints(self):
        """Load summoner constraints from YAML file"""
        # Try multiple possible locations for the YAML file
        possible_paths = [
            os.path.join(
                os.path.dirname(__file__),
                "../../data/summoner_constraints.yaml"
            ),
            os.path.join(
                os.path.dirname(__file__),
                "../data/summoner_constraints.yaml"
            ),
            os.path.join(
                os.getcwd(),
                "data/summoner_constraints.yaml"
            ),
            "/home/jbaucom/code/splinterlands_bot/data/summoner_constraints.yaml"
        ]
        
        constraints_file = None
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                constraints_file = abs_path
                break
        
        if constraints_file is None:
            print(f"Warning: summoner_constraints.yaml not found. Searched paths:")
            for path in possible_paths:
                print(f"  - {os.path.abspath(path)}")
            print("Summoner constraints disabled.")
            self._constraints = {}
            return
        
        try:
            with open(constraints_file, 'r') as f:
                self._constraints = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Error loading {constraints_file}: {e}")
            self._constraints = {}
    
    def get_max_monster_level(
        self,
        summoner_name: str,
        summoner_level: int,
        monster_rarity: int
    ) -> Optional[int]:
        """
        Get the max monster level this summoner can summon.
        Uses SummonerLevels.json which organizes constraints by rarity patterns.
        
        Args:
            summoner_name: Name of the summoner (e.g., "Kelya Frendul")
            summoner_level: Current level of the summoner (1-8)
            monster_rarity: Rarity of the monster (1=common, 2=rare, 3=epic, 4=legendary)
        
        Returns:
            Max monster level allowed, or None if not found in constraints
        """
        if not self._constraints:
            return None
        
        # Map rarity numbers to names
        rarity_names = {
            1: "common",
            2: "rare",
            3: "epic",
            4: "legendary",
        }
        
        if monster_rarity not in rarity_names:
            return None
        
        rarity_name = rarity_names[monster_rarity]
        summoner_level_str = str(summoner_level)  # Convert to string for YAML keys
        
        # Find the summoner's rarity from constraints
        summoner_rarity = None
        for section_name, summoners in self._constraints.items():
            if not isinstance(summoners, dict):
                continue
            if summoner_name in summoners:
                # Extract rarity from section name (e.g., "rare_summoners" -> "rare")
                if "_summoners" in section_name:
                    summoner_rarity = section_name.replace("_summoners", "")
                break
        
        if not summoner_rarity:
            # Summoner not found in constraints - load from SummonerLevels.json
            summoner_rarity = self._determine_summoner_rarity_from_json(summoner_name)
        
        if not summoner_rarity:
            return None
        
        # Load constraints from SummonerLevels.json
        try:
            levels_file = os.path.join(
                os.path.dirname(__file__),
                "../../data/SummonerLevels.json"
            )
            abs_path = os.path.abspath(levels_file)
            if os.path.exists(abs_path):
                with open(abs_path, 'r') as f:
                    import json
                    levels_data = json.load(f)
                    
                    # Get the constraint for this rarity and level
                    if summoner_rarity in levels_data:
                        level_dict = levels_data[summoner_rarity].get(summoner_level_str, {})
                        if rarity_name in level_dict:
                            return level_dict[rarity_name]
        except Exception as e:
            # Silently fail - constraints not available
            pass
        
        return None
    
    def _determine_summoner_rarity_from_json(self, summoner_name: str) -> Optional[str]:
        """
        Determine a summoner's rarity by looking it up in summoners.json.
        Returns the rarity string: 'common', 'rare', 'epic', or 'legendary'.
        """
        try:
            import json
            summoners_file = os.path.join(
                os.path.dirname(__file__),
                "../../data/summoners.json"
            )
            abs_path = os.path.abspath(summoners_file)
            if os.path.exists(abs_path):
                with open(abs_path, 'r') as f:
                    summoners = json.load(f)
                    
                    rarity_map = {1: 'common', 2: 'rare', 3: 'epic', 4: 'legendary'}
                    
                    for summoner in summoners:
                        if summoner.get('name') == summoner_name:
                            rarity_num = summoner.get('rarity', 2)
                            return rarity_map.get(rarity_num, 'rare')
        except Exception:
            pass
        
        return None
    
    def is_monster_allowed(
        self,
        summoner_name: str,
        summoner_level: int,
        monster_name: str,
        monster_level: int,
        monster_rarity: int
    ) -> bool:
        """
        Check if a monster is allowed to be summoned by this summoner.
        
        Args:
            summoner_name: Name of summoner
            summoner_level: Current level of summoner
            monster_name: Name of monster (for logging only)
            monster_level: Level of the monster
            monster_rarity: Rarity of the monster
        
        Returns:
            True if allowed, False if not
        """
        max_level = self.get_max_monster_level(summoner_name, summoner_level, monster_rarity)
        if max_level is None:
            # Constraints not found - allow by default
            return True
        
        return monster_level <= max_level

    def is_summoner_disabled(self, summoner_name: str) -> bool:
        """
        Check if a summoner is marked as disabled in the constraints file.
        
        Args:
            summoner_name: Name of the summoner (e.g., "Kelya Frendul")
        
        Returns:
            True if disabled, False otherwise
        """
        if not self._constraints:
            return False
        
        # Search through all summoner sections
        for section_name, summoners in self._constraints.items():
            if not isinstance(summoners, dict):
                continue
            if summoner_name in summoners:
                summoner_data = summoners[summoner_name]
                # Return the disable flag, default to False if not present
                return summoner_data.get('disable', False)
        
        return False

    def get_summoner_species(self, summoner_name: str) -> Optional[str]:
        """
        Get the species/race of a summoner for species-based bonuses.
        
        Args:
            summoner_name: Name of the summoner (e.g., "Kaylia Silverleaf")
        
        Returns:
            Species string (e.g., "Elf", "Human", "Dragon"), or None if not found
        """
        # Load species data from separate YAML file
        species_file = os.path.join(
            os.path.dirname(__file__),
            "../../data/summoner_species.yaml"
        )
        abs_path = os.path.abspath(species_file)
        
        if not os.path.exists(abs_path):
            return None
        
        try:
            with open(abs_path, 'r') as f:
                species_data = yaml.safe_load(f) or {}
                species_by_summoner = species_data.get('species_by_summoner', {})
                return species_by_summoner.get(summoner_name)
        except Exception:
            return None


# Global instance
_constraints_instance = None


def get_constraints() -> SummonerConstraints:
    """Get the global SummonerConstraints instance"""
    global _constraints_instance
    if _constraints_instance is None:
        _constraints_instance = SummonerConstraints()
    return _constraints_instance
