"""
Scrape summoner abilities from Splinterlands card pages.
Fetches ability data for all summoners and saves to data/summoner_abilities.yaml
"""

import requests
from bs4 import BeautifulSoup
import yaml
import time
from splinterlands.api.cards import get_player_cards, get_card_details

def scrape_summoner_abilities(username: str):
    """
    Scrape summoner abilities from Splinterlands website for all player summoners.
    """
    # Get player's summoner cards
    owned_cards = get_player_cards(username)
    details = get_card_details()
    details_map = {d["id"]: d for d in details}
    
    summoner_cards = {}
    for card in owned_cards:
        detail = details_map.get(card["card_detail_id"])
        if not detail:
            continue
        
        # Check if it's a summoner
        if detail.get("type") != "Summoner":
            continue
        
        card_id = card["card_detail_id"]
        if card_id not in summoner_cards:
            summoner_cards[card_id] = {
                "id": card_id,
                "name": detail.get("name"),
                "color": detail.get("color"),
                "rarity": detail.get("rarity"),
            }
    
    print(f"Found {len(summoner_cards)} unique summoner cards")
    
    # Scrape abilities for each summoner
    abilities_data = {}
    
    for card_id, info in summoner_cards.items():
        name = info["name"]
        color = info["color"]
        rarity = info["rarity"]
        
        url = f"https://splinterlands.com/card-detail/{card_id}/"
        try:
            print(f"Scraping {name} (ID {card_id})...", end=" ", flush=True)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for ability text - typically in a specific section
            abilities_text = []
            
            # Try to find text like "+1 armor" or "+1 speed"
            for text in soup.stripped_strings:
                if any(keyword in text.lower() for keyword in ['+1', '+2', 'ability', 'armor', 'speed', 'health', 'attack', 'magic', 'ranged', 'melee', 'heal', 'shield']):
                    if 'level' not in text.lower() and 'chaos' not in text.lower() and 'circulation' not in text.lower():
                        abilities_text.append(text)
            
            # Try to extract from common patterns
            ability_section = None
            for idx, elem in enumerate(soup.find_all(['p', 'div', 'span'])):
                text = elem.get_text().strip()
                if '+' in text and any(word in text.lower() for word in ['armor', 'speed', 'health', 'attack']):
                    ability_section = text
                    break
            
            if ability_section:
                print(f"Found: {ability_section}")
                abilities_data[name] = {
                    "id": card_id,
                    "color": color,
                    "rarity": rarity,
                    "abilities": ability_section
                }
            else:
                print("No abilities found")
                abilities_data[name] = {
                    "id": card_id,
                    "color": color,
                    "rarity": rarity,
                    "abilities": None
                }
            
            # Rate limit to avoid hammering the server
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error: {e}")
            abilities_data[name] = {
                "id": card_id,
                "color": color,
                "rarity": rarity,
                "abilities": None
            }
    
    # Save to file
    with open('data/summoner_abilities.yaml', 'w') as f:
        yaml.dump(abilities_data, f, default_flow_style=False, sort_keys=False)
    
    print("\n✅ Saved to data/summoner_abilities.yaml")
    return abilities_data

if __name__ == "__main__":
    scrape_summoner_abilities('tardigrade123')
