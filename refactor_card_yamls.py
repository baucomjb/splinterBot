"""
Refactor card YAML files to split summoners/monsters and consolidate mana data.

Changes:
1. Extract mana from array to single value
2. Move mana to directly under name (only once)
3. Keep other fields as they are
4. Create separate {color}_summoners.yaml and {color}_monsters.yaml files
"""

import yaml
import os
from pathlib import Path

def refactor_card_yamls():
    """Refactor all card YAML files in data/processed/"""
    
    data_dir = Path("data/processed")
    colors = ['black', 'blue', 'green', 'red', 'white', 'neutral']
    
    for color in colors:
        yaml_file = data_dir / f"{color}.yaml"
        if not yaml_file.exists():
            print(f"⚠️  {color}.yaml not found, skipping")
            continue
        
        print(f"\nProcessing {color}.yaml...")
        
        # Load original YAML
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f) or {}
        
        # Get summoners and monsters
        summoners = data.get('summoners', [])
        monsters = data.get('monsters', [])
        
        if not summoners and not monsters:
            print(f"  No cards found in {color}.yaml")
            continue
        
        # Refactor summoners
        if summoners:
            refactored_summoners = [refactor_card(card) for card in summoners]
            summoners_file = data_dir / f"{color}_summoners.yaml"
            with open(summoners_file, 'w') as f:
                yaml.dump(refactored_summoners, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(f"  ✅ Created {color}_summoners.yaml with {len(refactored_summoners)} summoners")
        
        # Refactor monsters
        if monsters:
            refactored_monsters = [refactor_card(card) for card in monsters]
            monsters_file = data_dir / f"{color}_monsters.yaml"
            with open(monsters_file, 'w') as f:
                yaml.dump(refactored_monsters, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(f"  ✅ Created {color}_monsters.yaml with {len(refactored_monsters)} monsters")


def refactor_card(card):
    """
    Refactor a single card:
    - Convert mana from array to single value
    - Move mana right under name
    - Keep other fields intact
    """
    cleaned = {}
    
    # Add name first
    if 'name' in card:
        cleaned['name'] = card['name']
    
    # Extract mana from array to single value
    if 'mana' in card:
        mana_val = card['mana']
        if isinstance(mana_val, list) and len(mana_val) > 0:
            # Get first value (they're all the same)
            cleaned['mana'] = mana_val[0]
        elif isinstance(mana_val, int):
            cleaned['mana'] = mana_val
    
    # Copy all other fields (except mana which we already processed)
    for key, value in card.items():
        if key not in ['name', 'mana']:
            cleaned[key] = value
    
    return cleaned


if __name__ == "__main__":
    refactor_card_yamls()
    print("\n✅ Card YAML refactoring complete!")
