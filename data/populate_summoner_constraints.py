#!/usr/bin/env python3
"""
Populate summoner_constraints.yaml with all summoners from player_cards.json
Organizes them by rarity and card set.
"""

import json
import yaml
from pathlib import Path
from collections import defaultdict

def populate_summoner_constraints():
    """Load player cards, extract summoners, and create constraints file."""
    
    # Load data
    with open('data/player_cards.json', 'r') as f:
        player_data = json.load(f)
    
    with open('data/summoners.json', 'r') as f:
        all_summoners = json.load(f)
    
    # Create lookup map
    summoner_lookup = {s['card_detail_id']: s for s in all_summoners}
    
    # Extract unique summoners owned  
    summoners_by_rarity = defaultdict(list)
    seen = set()
    
    for card in player_data['cards']:
        card_id = card['card_detail_id']
        card_set = card.get('card_set', 'unknown')
        
        if card_id in summoner_lookup and card_id not in seen:
            summoner = summoner_lookup[card_id]
            rarity = summoner['rarity']
            rarity_names = {1: 'common', 2: 'rare', 3: 'epic', 4: 'legendary'}
            rarity_name = rarity_names.get(rarity, f'unknown_rarity_{rarity}')
            
            summoner_info = {
                'name': summoner['name'],
                'card_detail_id': card_id,
                'color': summoner['splinter'],
                'rarity': rarity_name,
                'card_set': card_set
            }
            summoners_by_rarity[rarity_name].append(summoner_info)
            seen.add(card_id)
    
    # Build YAML structure
    yaml_data = {
        'note': 'Summoner collection metadata. Card constraints are in SummonerLevels.json',
        'summoners': {}
    }
    
    rarity_order = ['common', 'rare', 'epic', 'legendary']
    
    for rarity in rarity_order:
        if rarity not in summoners_by_rarity:
            continue
        
        rarity_key = f'{rarity}_summoners'
        yaml_data['summoners'][rarity_key] = {}
        
        # Sort by name for readability
        summoners = sorted(summoners_by_rarity[rarity], key=lambda x: x['name'])
        
        for summoner in summoners:
            yaml_data['summoners'][rarity_key][summoner['name']] = {
                'card_detail_id': summoner['card_detail_id'],
                'color': summoner['color'],
                'card_set': summoner['card_set']
            }
    
    # Write to file
    output_path = Path('data/summoner_constraints.yaml')
    with open(output_path, 'w') as f:
        yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Print summary
    total = sum(len(v) for v in summoners_by_rarity.values())
    print(f"✓ Updated {output_path}")
    print(f"  Total summoners: {total}")
    for rarity in rarity_order:
        if rarity in summoners_by_rarity:
            count = len(summoners_by_rarity[rarity])
            print(f"  - {rarity.capitalize()}: {count}")

if __name__ == "__main__":
    populate_summoner_constraints()
