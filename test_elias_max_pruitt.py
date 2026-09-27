#!/usr/bin/env python3
"""
Test script to force selection of Elias Max Pruitt (multi-color summoner)
and see if cards from both White and Blue splinters are selected.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from splinterlands.game.card_pool import CardPool
from splinterlands.game.battle_state import BattleState
from splinterlands.strategy.rule_engine import WaterBot, TeamSelectionLogger
from datetime import datetime
import random

def test_elias_max_pruitt():
    """Test multi-color summoner Elias Max Pruitt"""
    
    logger = TeamSelectionLogger(enable_file_logging=True)
    
    print("="*70)
    print("🧪 TESTING ELIAS MAX PRUITT (Multi-Color Summoner)")
    print("="*70)
    
    # Load card pool
    manager = CardPool("tardigrade123")
    pool = manager.get_card_pool()
    print(f"✓ Loaded {len(pool)} cards")
    
    # Create mock battle
    battle_state = BattleState(
        battle_id="elias_test_001",
        mana_cap=40,
        rulesets=[],
        allowed_splinters=['White', 'Blue', 'Dragon', 'Fire', 'Death', 'Earth', 'Life']
    )
    
    print(f"✓ Battle ID: {battle_state.battle_id}")
    print(f"✓ Mana Cap: {battle_state.mana_cap}")
    print(f"✓ Allowed Splinters: {battle_state.allowed_splinters}")
    print()
    
    # Get all Elias Max Pruitt in the pool
    elias_cards = [c for c in pool if c.name == 'Elias Max Pruitt']
    print(f"Found {len(elias_cards)} Elias Max Pruitt card(s)")
    
    if not elias_cards:
        print("❌ Elias Max Pruitt not found in card pool!")
        return
    
    elias = elias_cards[0]
    print(f"Using: {elias.name} (Level {elias.level}, Colors: {elias.colors if hasattr(elias, 'colors') else elias.color})")
    print()
    
    # Run team selection with Elias forced as summoner
    logger.log("\n" + "="*60)
    logger.log("📊 TEAM SELECTION TEST - ELIAS MAX PRUITT")
    logger.log("="*60 + "\n")
    
    logger.log(f"Summoner: {elias.name} (Level {elias.level})")
    logger.log(f"Summoner Splinters: White + Blue")
    logger.log(f"Mana Cap: {battle_state.mana_cap}")
    logger.log(f"Allowed Splinters: {battle_state.allowed_splinters}\n")
    
    # Get available cards for team selection (all non-summoner cards)
    available = [c for c in pool if c.type != "Summoner"]
    
    # Select team using Elias
    monsters = WaterBot.select_monsters(
        available=available,
        summoner=elias,
        mana_cap=battle_state.mana_cap,
        rulesets=battle_state.rulesets,
        num_slots=5,
        logger=logger
    )
    
    logger.log("\n✅ TEAM COMPOSITION")
    logger.log("="*60)
    
    summoner_mana = WaterBot._get_estimated_mana_cost(elias)
    total_monster_mana = sum(WaterBot._get_estimated_mana_cost(m) for m in monsters)
    total_mana = summoner_mana + total_monster_mana
    
    logger.log(f"\nSummoner: {elias.name} (Lvl {elias.level}) - Mana: {summoner_mana}")
    logger.log(f"Monsters ({len(monsters)}) - Mana: {total_monster_mana}")
    logger.log(f"Total Mana: {total_mana}/{battle_state.mana_cap}\n")
    
    # Analyze splinter distribution
    splinter_count = {}
    for i, m in enumerate(monsters, 1):
        color = m.color
        if color not in splinter_count:
            splinter_count[color] = []
        splinter_count[color].append(m.name)
        logger.log(f"{i}. {m.name:25} | {color:8} | Lvl {m.level} | Mana {WaterBot._get_estimated_mana_cost(m)}")
    
    logger.log(f"\n📊 SPLINTER BREAKDOWN:")
    for color, cards in sorted(splinter_count.items()):
        logger.log(f"   {color:8} : {len(cards)} cards")
    
    # Check if both splinters are represented
    logger.log("\n✅ TEST RESULTS:")
    if 'White' in splinter_count and 'Blue' in splinter_count:
        logger.log("   ✓ Both White AND Blue splinter cards selected!")
        logger.log("   ✓ Multi-color summoner is working correctly!")
    else:
        logger.log("   ⚠ Only one splinter represented in team")
        logger.log(f"   ⚠ Splinters selected: {list(splinter_count.keys())}")
    
    logger.log("\n" + "="*60 + "\n")
    
    # Save logs
    filepath = logger.save()
    if filepath:
        logger.log(f"📝 Test log saved to: {filepath}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_elias_max_pruitt()
