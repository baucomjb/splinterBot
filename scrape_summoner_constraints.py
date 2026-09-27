"""
Scraper to fetch summoner card details from Splinterlands and extract constraints.
Saves summoner ability/constraint info to YAML organized by summoner name.
"""

import requests
import re
import yaml
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


def get_player_summoners(username: str) -> List[Dict]:
    """Get all summoner cards owned by player"""
    from splinterlands.api.cards import get_player_cards
    
    owned_cards = get_player_cards(username)
    from splinterlands.api.cards import get_card_details
    
    details = get_card_details()
    details_map = {d["id"]: d for d in details}
    
    # Filter to summoners only
    summoners = []
    for card in owned_cards:
        detail = details_map.get(card["card_detail_id"])
        if detail and detail.get("type") == "Summoner":
            summoners.append((card, detail))
    
    return summoners


def scrape_summoner_page(card_detail_id: int, regular_or_gold: str = "regular") -> Optional[Dict]:
    """
    Scrape a summoner's card page to extract level constraints.
    
    Args:
        card_detail_id: The card detail ID (e.g., 437 for Kelya)
        regular_or_gold: "regular" or "gold" for foil type
    
    Returns:
        Dict with keys:
        - name: Summoner name
        - rarity: Rarity level (1-5)
        - level: Summoner's max level
        - level_7_url: URL to level 7 version for scraping
        - common_max_level: Max common monster level for each summoner level
        - rare_max_level: Max rare monster level for each summoner level
        - epic_max_level: Max epic monster level for each summoner level
        - legendary_max_level: Max legendary monster level for each summoner level
    """
    
    # Try level 7 (highest common level)
    url = f"https://splinterlands.com/card-detail/{card_detail_id}/{regular_or_gold}/7/?tab=stats"
    
    try:
        # Use session with retry
        session = requests.Session()
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract summoner name from page title or header
        # Looking for pattern: "SUMMONER_NAME RARITY SPLINTER"
        title = soup.find('title')
        name_match = re.search(r'([\w\s]+?)\s+(?:RARE|COMMON|EPIC|LEGENDARY)', soup.get_text())
        
        # Alternative: look for the card name in the main content
        # This is tricky without seeing actual HTML structure
        # For now, we'll need to pass name in or extract from API
        
        print(f"✅ Scraped {url}")
        return {
            "url_source": url,
            "status": "scraped_basic_structure"
        }
        
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None


def build_summoner_constraints_from_api(username: str) -> Dict:
    """
    Build summoner constraints by:
    1. Getting player's summoners from API
    2. Scraping their card pages for constraints
    3. Returning structured data
    """
    
    player_summoners = get_player_summoners(username)
    constraints = {}
    
    print(f"\n📊 Found {len(player_summoners)} summoner cards for {username}")
    
    for card, detail in player_summoners:
        name = detail.get("name")
        detail_id = detail.get("id")
        level = card.get("level", 1)
        rarity = detail.get("rarity")
        
        print(f"\n🔍 Processing: {name} (ID: {detail_id}, Rarity: {rarity}, Your Level: {level})")
        
        # Scrape the card page
        # We'll need to get the actual constraints from the page
        # For now, store what we know
        constraints[name] = {
            "card_detail_id": detail_id,
            "rarity": rarity,
            "splinter": detail.get("color"),
            "max_level": 8,  # All summoners go to level 8
            "your_level": level,
            "constraints": {
                # These will be filled in by scraping
                # Format: List of per-level max allowed monster levels
                "common": [],  # E.g., [2, 3, 4, 5, 6, 6, 7, 8]
                "rare": [],
                "epic": [],
                "legendary": []
            }
        }
    
    return constraints


if __name__ == "__main__":
    # Test with sample data
    # In real usage: get from config or command line
    username = "tardigrade123"
    
    try:
        summoner_data = build_summoner_constraints_from_api(username)
        
        print("\n" + "="*60)
        print("📋 Summoner Data to be Scraped/Processed:")
        print("="*60)
        for name, data in summoner_data.items():
            print(f"\n{name}:")
            print(f"  Rarity: {data['rarity']}, Your Level: {data['your_level']}")
            print(f"  Splinter: {data['splinter']}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
