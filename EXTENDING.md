# Extending the Bot - Custom Strategies Guide

## How to Add New Splinter Strategies

The bot is modular by design. Adding a new splinter strategy is straightforward.

### Step 1: Create a New Strategy Class

Add to `splinterlands/strategy/rule_engine.py`:

```python
class FireBot:
    """Fire splinter focused strategy"""
    
    FIRE_SUMMONERS = {
        "Tarsa", "Molten Ogre", "Radiated Brute",
        # Add more fire summoners
    }
    
    FIRE_CARDS = {
        "Kobold Miner", "Creeping Ooze", "Serpent of Eld",
        # Add more fire cards
    }
    
    @staticmethod
    def filter_fire_cards(pool: List[Card]) -> List[Card]:
        """Filter card pool to fire splinter only cards"""
        fire_cards = []
        for card in pool:
            if card.type == "Summoner":
                if card.name in FireBot.FIRE_SUMMONERS:
                    fire_cards.append(card)
            elif card.color == "Red":  # Fire splinter cards are red
                if card.name in FireBot.FIRE_CARDS or card.type == "Monster":
                    fire_cards.append(card)
        return fire_cards
    
    # ... add same methods as WaterBot
```

### Step 2: Create a Strategy Router

Replace the simple `choose_team()` function with a router:

```python
def choose_team(battle_state, card_pool: List[Card]) -> Optional[Tuple]:
    """
    Route to appropriate strategy based on allowed splinters
    """
    
    allowed = battle_state.allowed_splinters
    
    # Try strategies in order of preference
    if "Water" in allowed:
        return _choose_water_team(battle_state, card_pool)
    elif "Fire" in allowed:
        return _choose_fire_team(battle_state, card_pool)
    elif "Earth" in allowed:
        return _choose_earth_team(battle_state, card_pool)
    elif "Life" in allowed:
        return _choose_life_team(battle_state, card_pool)
    elif "Death" in allowed:
        return _choose_death_team(battle_state, card_pool)
    elif "Dragon" in allowed:
        return _choose_dragon_team(battle_state, card_pool)
    else:
        print("❌ No splinters available")
        return None

def _choose_water_team(battle_state, card_pool):
    """Water strategy implementation"""
    # ... existing WaterBot code
    pass

def _choose_fire_team(battle_state, card_pool):
    """Fire strategy implementation"""
    # ... FireBot code
    pass
```

## Advanced: Opponent-Aware Strategy

Track opponent patterns and adjust:

```python
class OpponentAnalyzer:
    """Analyze opponent deck patterns"""
    
    def __init__(self, username: str):
        self.username = username
        self.recent_battles = []  # Store last N battles
    
    def load_recent_battles(self, count: int = 10):
        """Load recent battle results from API"""
        # Query battle history
        # Filter out wins/losses vs different splinters
        pass
    
    def get_most_used_splinters(self) -> List[str]:
        """Return opponent's favorite splinters"""
        pass
    
    def get_strong_vs(self, splinter: str) -> List[Card]:
        """Get cards that counter opponent's splinter"""
        pass

# Use in choose_team:
analyzer = OpponentAnalyzer(opponent_name)
analyzer.load_recent_battles()
strong_splinters = analyzer.get_most_used_splinters()
# Counter-pick splinter
```

## Advanced: Machine Learning Win Prediction

```python
class WinPredictor:
    """Predict battle outcome before submission"""
    
    def __init__(self):
        self.model = None
    
    def train_from_history(self, battle_history: List[Dict]):
        """Train on past battles"""
        # Extract features: team composition, mana, rulesets
        # Labels: won/lost
        # Use scikit-learn or similar
        pass
    
    def predict_win_probability(
        self,
        your_team: Team,
        battle_state: BattleState,
        opponent: Dict
    ) -> float:
        """
        Predict win probability (0.0-1.0)
        """
        features = self._extract_features(your_team, battle_state)
        probability = self.model.predict_proba(features)[0][1]
        return probability
    
    def _extract_features(self, team: Team, state: BattleState) -> List[float]:
        """Convert team to feature vector"""
        return [
            len(team.monsters),
            sum(m.stats.health for m in team.monsters),
            sum(m.stats.armor for m in team.monsters),
            # ... more features
        ]
```

## Ruleset-Specific Strategies

Handle special ruleset combinations:

```python
class RulesetHandler:
    """Special handling for complex rulesets"""
    
    SNEAK = "Sneak"  # Attacks backmost enemy
    FLYING = "Flying"  # Can't be attacked by melee/ranged
    THORNS = "Thorns"  # Damages attacker
    AMPLIFY = "Amplify"  # Damage increases by 1
    
    @staticmethod
    def get_strategy_for_rulesets(rulesets: List[str]) -> str:
        """Recommend strategy based on rulesets"""
        
        if "Sneak" in rulesets:
            # Position tank at back, damage dealers in front
            return "sneak_focus"
        
        if "Flying" in rulesets:
            # Maximize ranged damage, melee useless
            return "ranged_focus"
        
        if "Thorns" in rulesets:
            # Low damage output, magic focus
            return "magic_focus"
        
        return "balanced"

# Use in team selection:
strategy_hint = RulesetHandler.get_strategy_for_rulesets(battle_state.rulesets)
monsters = WaterBot.select_monsters(
    available,
    battle_state.mana_cap,
    battle_state.rulesets,
    strategy=strategy_hint
)
```

## Scheduling & Automation

Run bot automatically:

```python
# scheduler.py
import schedule
import time
from bot import run_bot_loop

def schedule_bot():
    """Run bot every 5 minutes"""
    
    # Run immediately
    run_bot_loop()
    
    # Schedule repeating
    schedule.every(5).minutes.do(run_bot_loop)
    
    # Keep scheduler alive
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    schedule_bot()
```

Or using APScheduler for more control:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from bot import run_bot_loop
import atexit

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=run_bot_loop,
    trigger="interval",
    minutes=5,
    id='bot_worker',
    name='Run bot every 5 minutes',
    replace_existing=True
)

scheduler.start()
atexit.register(lambda: scheduler.shutdown())
```

## Card Collection Management

Track and update your card pool:

```python
class CardCollection:
    """Persistent card collection cache"""
    
    def __init__(self, username: str, cache_file: str = "card_pool.json"):
        self.username = username
        self.cache_file = cache_file
        self.cards = []
        self.last_updated = None
    
    def load_from_cache(self):
        """Load previously saved cards"""
        import json
        with open(self.cache_file, 'r') as f:
            data = json.load(f)
            self.cards = data['cards']
            self.last_updated = data['updated']
    
    def save_to_cache(self):
        """Save cards to local cache"""
        import json
        with open(self.cache_file, 'w') as f:
            json.dump({
                'cards': [c.__dict__ for c in self.cards],
                'updated': datetime.now().isoformat()
            }, f)
    
    def refresh_if_stale(self, max_age_hours: int = 1):
        """Only refresh if cache is older than threshold"""
        import datetime
        if not self.last_updated:
            self.refresh()
            return
        
        age = datetime.datetime.now() - datetime.datetime.fromisoformat(self.last_updated)
        if age.total_seconds() > max_age_hours * 3600:
            self.refresh()
    
    def refresh(self):
        """Fetch fresh card pool from API"""
        self.cards = build_card_pool(self.username)
        self.save_to_cache()
```

## Battle Statistics Tracking

Record outcomes for analysis:

```python
class BattleStatistics:
    """Track battle statistics for learning"""
    
    def __init__(self, username: str, db_file: str = "battles.db"):
        self.username = username
        self.db_file = db_file
    
    def record_battle(self, team: Team, result: Dict):
        """Record battle outcome"""
        import sqlite3
        import json
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO battles 
            (username, battle_id, team_json, win, reward, timestamp)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (
            self.username,
            team.battle_id,
            json.dumps(team.to_submission_dict()),
            result.get('won'),
            result.get('reward', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def get_win_rate(self, splinter: str = None) -> float:
        """Calculate win rate by splinter"""
        # Query battles by splinter, count wins
        pass
```

## Configuration Enhancement

Extend config for strategy control:

```yaml
account:
  username: "tardigrade123"
  posting_key: "your_key"

bot:
  mode: "wild"
  log_level: "info"
  
  # Strategy selection
  strategy: "auto"  # or "water", "fire", "earth", etc.
  
  # Ruleset preferences
  ruleset_strategies:
    sneak: "magic_based"
    flying: "ranged_focus"
    thorns: "summoner_spam"
  
  # Scheduling
  auto_battle: true
  check_interval_seconds: 300  # Check every 5 minutes
  
  # Learning
  track_battles: true
  enable_predictions: false
  
  # Constraints
  min_win_probability: 0.5  # Don't submit if < 50% win chance
  max_battles_per_hour: 12
```

## Testing Your Strategy

```python
def test_water_bot():
    """Unit test your strategy"""
    from unittest.mock import Mock
    
    # Create mock battle state
    battle_state = Mock()
    battle_state.mana_cap = 45
    battle_state.rulesets = []
    battle_state.allowed_splinters = ["Water"]
    
    # Create mock cards
    summoner = Mock(spec=Card)
    summoner.type = "Summoner"
    summoner.name = "Kelya Frendul"
    
    monsters = [Mock(spec=Card, type="Monster") for _ in range(3)]
    
    card_pool = [summoner] + monsters
    
    # Test strategy
    result = choose_team(battle_state, card_pool)
    
    assert result is not None
    assert len(result[1]) <= 5
    print("✅ Water bot test passed")

if __name__ == "__main__":
    test_water_bot()
```

---

## Summary

Your bot is extensible! You can:
- ✅ Add new splinter strategies (copy WaterBot pattern)
- ✅ Implement opponent analysis
- ✅ Add ML-based win prediction
- ✅ Handle special rulesets
- ✅ Schedule automatic battles
- ✅ Track statistics for improvement
- ✅ Use different strategies per ruleset

Start with one strategy and expand from there!
