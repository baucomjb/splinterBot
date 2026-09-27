#!/usr/bin/env python3
"""
Script to simplify colored summoner YAML files by removing unnecessary fields.
Summoners don't battle (no combat stats) and abilities don't change by level 
(stored in summoner_abilities.yaml instead).
Keeps only: name, mana, level, copies, rarity, gold
"""

import yaml
import os
from pathlib import Path

# Target files in processed directory
processed_dir = Path(__file__).parent / "data" / "processed"
color_summoner_files = [
    "blue_summoners.yaml",
    "red_summoners.yaml",
    "green_summoners.yaml",
    "black_summoners.yaml",
    "white_summoners.yaml",
    "neutral_summoners.yaml",
]

# Fields to remove:
# - Combat stats: not used by summoners
# - abilities: stored in summoner_abilities.yaml, don't change by level
FIELDS_TO_REMOVE = ['attack', 'magic', 'ranged', 'speed', 'armor', 'health', 'abilities']

def simplify_summoner_file(filepath):
    """Load YAML, remove unnecessary fields, and save back."""
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r') as f:
        summoners = yaml.safe_load(f)
    
    if not summoners:
        print(f"  Warning: File is empty or invalid")
        return
    
    # Remove unnecessary fields from each summoner
    for summoner in summoners:
        for field in FIELDS_TO_REMOVE:
            if field in summoner:
                del summoner[field]
    
    # Write back to file with nice formatting
    with open(filepath, 'w') as f:
        yaml.dump(
            summoners,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        )
    
    print(f"  ✓ Removed {len(FIELDS_TO_REMOVE)} fields, keeping: name, mana, level, copies, rarity, gold")

if __name__ == "__main__":
    if not processed_dir.exists():
        # Adjust path - script is in /data/, processed is in /data/processed/
        processed_dir = Path(__file__).parent / "processed"
    
    print(f"Simplifying summoner YAML files in: {processed_dir}\n")
    
    for filename in color_summoner_files:
        filepath = processed_dir / filename
        if filepath.exists():
            simplify_summoner_file(filepath)
        else:
            print(f"Skipping: {filepath} (not found)")
    
    print(f"\n✓ Done! All summoner YAML files simplified.")

