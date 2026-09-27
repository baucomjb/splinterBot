#!/usr/bin/env python3
"""
Generate a team selection log using a mock battle to demonstrate
the summoner levels helper integration.
"""

from splinterlands.game.card_pool import build_card_pool
from splinterlands.game.battle_state import BattleState
from splinterlands.strategy.rule_engine import choose_team
import logging

# Set up basic logging to suppress debug output
logging.basicConfig(level=logging.ERROR)

def create_mock_player_data():
    """Create a properly formatted mock battle"""
    return {
        "battle": {
            "id": "test_battle_20260419_001",
            "mana_cap": "40",
            "ruleset": "",  # No special rules
            "inactive": "",  # All splinters allowed
            "opponent": "test_opponent"
        }
    }

def main():
    print("=" * 70)
    print("🧪 GENERATING TEAM SELECTION LOG")
    print("=" * 70)
    
    username = "tardigrade123"
    
    try:
        # Load card pool
        print(f"\n📚 Loading card pool for {username}...")
        card_pool = build_card_pool(username)
        print(f"   ✓ Loaded {len(card_pool)} cards")
        
        # Create mock battle state
        print("\n⚔️  Creating mock battle...")
        player_data = create_mock_player_data()
        battle_state = BattleState(player_data)
        print(f"   ✓ Battle ID: {battle_state.battle_id}")
        print(f"   ✓ Mana Cap: {battle_state.mana_cap}")
        print(f"   ✓ Allowed Splinters: {battle_state.allowed_splinters}")
        
        # Run team selection (this will create the log file)
        print("\n🎯 Running team selection (will generate logs)...")
        result = choose_team(battle_state, card_pool, verbose=True, save_log=True)
        
        if result:
            summoner, monsters = result
            print(f"\n✅ SUCCESS!")
            print(f"   Summoner: {summoner.name} (Level {summoner.level})")
            print(f"   Monsters: {len(monsters)} selected")
            print(f"\n📝 Team selection log has been saved to logs/ directory")
        else:
            print(f"\n❌ Team selection returned None")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")
