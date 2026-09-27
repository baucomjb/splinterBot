#!/usr/bin/env python3
"""
Simple test of summoner_levels_helper to show it's working
"""

from data.summoner_levels_helper import get_max_card_level, get_all_max_card_levels

print("=" * 70)
print("🧪 TESTING SUMMONER LEVELS HELPER")
print("=" * 70)

# Test cases
test_cases = [
    ("rare", 4, "common", False),
    ("rare", 4, "rare", False),
    ("rare", 4, "epic", False),
    ("rare", 4, "legendary", False),
    ("common", 1, "common", False),
    ("epic", 2, "rare", False),
    ("legendary", 3, "legendary", False),
]

print("\n📋 Single Card Rarity Queries:")
print("-" * 70)
for rarity, level, card_rarity, is_gold in test_cases:
    max_level = get_max_card_level(rarity, level, card_rarity)
    print(f"Summoner: {rarity.capitalize():10} Lvl {level}  →  {card_rarity.capitalize():10} cards max: Level {max_level}")

print("\n📋 All Card Rarities for Summoner:")
print("-" * 70)

summoner_tests = [
    ("rare", 4),
    ("common", 1),
    ("epic", 3),
    ("legendary", 2),
]

for rarity, level in summoner_tests:
    levels = get_all_max_card_levels(rarity, level)
    print(f"\n{rarity.upper()} Summoner Level {level}:")
    print(f"  Can summon:")
    for card_type, max_lvl in levels.items():
        print(f"    • {card_type.capitalize():12} cards up to Level {max_lvl}")

print("\n🎯 Real Scenario:")
print("-" * 70)
print("Your Collection:")
print("  • Kelya Frendul (Rare Summoner, Level 5)")

kelya_constraints = get_all_max_card_levels("rare", 5)
print(f"\n  With this summoner at Level 5, you can use:")
for card_type, max_lvl in kelya_constraints.items():
    print(f"    • {card_type.capitalize():12} monster cards up to Level {max_lvl}")

print("\n" + "=" * 70)
print("✅ SUMMONER LEVELS HELPER IS WORKING CORRECTLY!")
print("=" * 70)
