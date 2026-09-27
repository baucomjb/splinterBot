"""
Helper module to query summoner levels and determine max card levels they can summon.

Usage:
    from data.summoner_levels_helper import get_max_card_level, get_all_max_card_levels
    
    # Get max level for a specific card rarity
    max_level = get_max_card_level('rare', 4, 'common')  # Returns 5
    
    # Get all max levels for a summoner
    all_levels = get_all_max_card_levels('rare', 4)  # Returns {"common": 5, "rare": 4, ...}
"""

import json
import os

_SUMMONER_LEVELS_DATA = None


def _load_summoner_levels():
    """Load SummonerLevels.json data once and cache it."""
    global _SUMMONER_LEVELS_DATA
    
    if _SUMMONER_LEVELS_DATA is None:
        data_path = os.path.join(os.path.dirname(__file__), 'SummonerLevels.json')
        with open(data_path, 'r') as f:
            _SUMMONER_LEVELS_DATA = json.load(f)
    
    return _SUMMONER_LEVELS_DATA


def get_max_card_level(summoner_rarity, summoner_level, card_rarity):
    """
    Get the maximum level a summoner can summon for a specific card rarity.
    
    Args:
        summoner_rarity (str): Summoner rarity ('common', 'rare', 'epic', 'legendary')
        summoner_level (int or str): Summoner level (1-10 for most)
        card_rarity (str): Card rarity ('common', 'rare', 'epic', 'legendary')
    
    Returns:
        int: Maximum card level this summoner can summon, or None if not found
    
    Example:
        >>> get_max_card_level('rare', 4, 'common')
        5
    """
    data = _load_summoner_levels()
    summoner_level = str(summoner_level)
    
    try:
        return data[summoner_rarity][summoner_level][card_rarity]
    except KeyError:
        return None


def get_all_max_card_levels(summoner_rarity, summoner_level):
    """
    Get the maximum levels for all card rarities a summoner can summon.
    
    Args:
        summoner_rarity (str): Summoner rarity ('common', 'rare', 'epic', 'legendary')
        summoner_level (int or str): Summoner level (1-10 for most)
    
    Returns:
        dict: Dictionary with card rarities as keys and max levels as values
              {"common": X, "rare": Y, "epic": Z, "legendary": W}
              Returns empty dict if summoner not found
    
    Example:
        >>> get_all_max_card_levels('rare', 4)
        {'common': 5, 'rare': 4, 'epic': 3, 'legendary': 2}
    """
    data = _load_summoner_levels()
    summoner_level = str(summoner_level)
    
    try:
        return data[summoner_rarity][summoner_level]
    except KeyError:
        return {}

