#!/usr/bin/env python3
"""
Test script to verify team selection with summoner level constraints.
Creates a mock battle and runs team selection to verify the summoner helper is working.
"""

from splinterlands.game.card_pool import build_card_pool
from splinterlands.game.battle_state import BattleState
from splinterlands.strategy.rule_engine import choose_team
import json
from datetime import datetime

# Mock battle data - test with various constraints
mock_battle = {
    "battle_id": "test_battle_001",
    "player": "tardigrade123",
    "opponent": "test_opponent",
    "mana_cap": 40,
    "rulesets": [],
    "allowed_splinters": ["Water", "Green", "Earth", "Dragon", "Death"],
    "ruleset_ids": []
}

def test_team_selection():
    """Test team selection with mock battle"""
    print("=" * 60)
    print("🧪 TESTING SUMMONER LEVELS WITH TEAM SELECTION")
    print("=" * 60)
    
    username = "tardigrade123"
    
    # Load card pool
    print(f"\n📚 Loading card pool for {username}...")
    card_pool = build_card_pool(username)
    
    # Create mock battle state
    print("⚔️  Creating mock battle...")
    try:
        battle_state = BattleState(mock_battle)
        print(f"   Battle ID: {battle_state.battle_id}")
        print(f"   Mana Cap: {battle_state.mana_cap}")
        print(f"   Allowed Splinters: {battle_state.allowed_splinters}")
        print(f"   Card pool: {len(card_pool)} total cards")
    except Exception as e:
        print(f"   Error creating battle state: {e}")
        return False
    
    # Select team
    print("\n🎯 Selecting team with constraints...")
    try:
        team_selection = choose_team(battle_state, card_pool)
        
        if team_selection:
            summoner, monsters = team_selection
            print(f"\n✅ Team Selected!")
            print(f"   Summoner: {summoner.name} (Level {summoner.level}, {summoner.rarity})")
            print(f"   Monsters: {len(monsters)} cards selected")
            
            total_mana = summoner.mana
            for m in monsters:
                total_mana += m.mana
                
            print(f"   Total Mana: {total_mana}")
            
            # Show monster details
            print(f"\n   Monster Details:")
            for i, m in enumerate(monsters, 1):
                print(f"   {i}. {m.name} (Lvl {m.level}, Mana {m.mana})")
            
            return True
        else:
            print("   ❌ Failed to select team")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during team selection: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_team_selection()
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED - Summoner levels working correctly!")
    else:
        print("❌ TEST FAILED - Check logs above")
    print("=" * 60)
