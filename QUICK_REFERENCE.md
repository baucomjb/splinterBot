# Quick Reference Guide

## Running the Bot

```bash
# Run a single bot cycle
python bot.py

# With debug logging
# Edit config/config.yaml and set log_level: "debug"
python bot.py

# Check for syntax errors
python -m py_compile bot.py
```

## Testing Individual Components

```python
# Test account download
from splinterlands.game.account import Account

account = Account("your_username")
account.download()
print(account.summary())

# Test card pool
from splinterlands.game.card_pool import build_card_pool

cards = build_card_pool("your_username")
print(f"Total cards: {len(cards)}")
for card in cards[:5]:
    print(card.summary())

# Test water bot strategy
from splinterlands.strategy.rule_engine import choose_team
from splinterlands.game.battle_state import BattleState

team = choose_team(battle_state, card_pool)
if team:
    summoner, monsters = team
    print(f"Selected: {summoner.name} + {len(monsters)} monsters")
```

## Common Issues & Solutions

### Issue: "No water cards in pool"
**Solution:** Your water splinter cards are all on sale or delegated. Check card statuses.

### Issue: "Water splinter not allowed"
**Solution:** Battle doesn't allow Water in this round. Bot waits for next battle.

### Issue: "Submission failed: Signature error"
**Solution:** Check posting_key in config.yaml - must be exact key from your Splinterlands account.

### Issue: "No active battle"
**Solution:** Normal - you need to be matched in a battle first. Bot will check again next run.

### Issue: API timeout
**Solution:** Splinterlands API may be slow. Try again in a few seconds.

## File Structure Quick Guide

```
bot.py                          ← ENTRY POINT (run this)
config/config.yaml              ← EDIT YOUR CREDENTIALS HERE
│
├─ splinterlands/
│  ├─ api/
│  │  ├─ client.py              ← API endpoints (account, battle, team)
│  │  └─ cards.py               ← Card collection & details APIs
│  │
│  ├─ game/
│  │  ├─ account.py             ← Account class (stats, quests, wins)
│  │  ├─ battle_state.py         ← BattleState (mana, rulesets)
│  │  ├─ card.py                ← Card class (individual card data)
│  │  ├─ card_pool.py            ← build_card_pool() function
│  │  ├─ stats.py               ← Stats class (health, armor, speed, etc)
│  │  └─ team.py                ← Team & TeamManager classes
│  │
│  └─ strategy/
│     └─ rule_engine.py         ← Team selection strategies
│
├─ README_BOT.md                ← Feature overview
├─ ARCHITECTURE.md              ← System design & data flow
└─ EXTENDING.md                 ← How to add new features
```

## Key Classes

### Account
```python
account = Account(username)
account.download()                    # Fetch all data from API
account.get_dec_balance()             # Float: DEC amount
account.get_rating()                  # Int: Current rating
account.get_season_info()             # Dict: Wins/losses
account.get_active_quest()            # Dict or None
account.has_active_battle()           # Bool
account.summary()                     # Formatted string
```

### Card
```python
card.uid                              # Unique identifier
card.name                             # "Fire Dragon"
card.type                             # "Monster" or "Summoner" or "Spell"
card.color                            # "Red", "Blue", "Green", etc.
card.level                            # 1-11 (max)
card.stats                            # Stats object
  .melee, .ranged, .magic             # Attack types (0-10)
  .armor, .health                     # Defense (0-100+)
  .speed                              # Speed (0-10)
card.abilities                        # List of ability strings
card.summary()                        # Formatted display
```

### BattleState
```python
state = BattleState(player_battle_data)
state.battle_id                       # "abc123..."
state.mana_cap                        # Int: 15-99
state.rulesets                        # List: ["Melee Only", "Armor Up"]
state.allowed_splinters               # List: ["Water", "Fire", ...]
state.opponent                        # Dict: opponent info
state.summary()                       # Dict summary
```

### Team
```python
team = Team(battle_id, summoner_card, [monster_cards])
team.splinter                         # e.g., "Water"
team.to_submission_dict()             # API payload format
team.summary()                        # Formatted display
```

### TeamManager
```python
manager = TeamManager(username, posting_key)
team = manager.create_team(battle_id, summoner, monsters)
manager.submit_team(team)             # Returns API response
manager.submit_and_confirm(team)      # Returns True/False
```

### WaterBot
```python
water_pool = WaterBot.filter_water_cards(card_pool)
summoner = WaterBot.select_summoner(water_pool)
monsters = WaterBot.select_monsters(
    available,
    mana_cap=45,
    rulesets=["Melee Only"],
    num_slots=5
)
```

## API Endpoints Reference

| Endpoint | Purpose |
|----------|---------|
| `GET /players/details?name=username` | Current battle & basic stats |
| `GET /players/profile?name=username` | Full profile (rating, DEC, record) |
| `GET /quests/get_active?username=username` | Active quest |
| `GET /cards/collection/username` | Your card collection |
| `GET /cards/get_details` | All card metadata |
| `POST /battle/submit_team` | Submit selected team |
| `GET /battle/result?id=battle_id` | Completed battle details |

## Configuration Template

```yaml
account:
  username: "your_splinterlands_username"
  posting_key: "your_posting_key_from_hive_keychain"

bot:
  mode: "wild"                    # Game mode
  log_level: "info"               # info, debug, warning, error
```

## Environment Variables (Optional)

You could enhance bot.py to support env vars:

```python
import os

username = os.getenv("SPLINTERLANDS_USERNAME") or config["account"]["username"]
posting_key = os.getenv("SPLINTERLANDS_POSTING_KEY") or config["account"]["posting_key"]
```

Then run:
```bash
export SPLINTERLANDS_USERNAME="your_username"
export SPLINTERLANDS_POSTING_KEY="your_key"
python bot.py
```

## Monitoring/Logging

View logs while running:
```bash
# Run with real-time logging
python bot.py 2>&1 | tee bot.log

# View tail of logs
tail -f bot.log

# Search logs for errors
grep "ERROR\|FAILED\|❌" bot.log
```

## Water Splinter Color Key

In Splinterlands:
- **Water** = Blue cards (color: "Blue")
- **Fire** = Red cards (color: "Red")
- **Earth** = Green cards (color: "Green")
- **Life** = White cards (color: "White")
- **Death** = Black cards (color: "Black")
- **Dragon** = Multi-color cards

Check actual colors in your client to verify!

## Performance Tips

1. **Cache card pool** - Don't fetch every run
   ```python
   import json
   # Save: json.dump(cards, open("cards.json", "w"))
   # Load: cards = json.load(open("cards.json"))
   ```

2. **Batch API calls** - Group queries when possible

3. **Use logging** - Track what's happening
   ```python
   import logging
   logging.info("About to submit team")
   ```

4. **Add timeouts** - Already in client.py (10s default)

5. **Check API status** - Look for rate limits in responses

## Next Steps Checklist

- [ ] Update config.yaml with your credentials
- [ ] Run `python bot.py` to test
- [ ] Verify account data downloads successfully
- [ ] Wait for active battle or manually start one
- [ ] Check if water cards are available
- [ ] Verify team submission succeeds
- [ ] Expand to other splinter strategies (see EXTENDING.md)
- [ ] Add scheduling for automatic battles
- [ ] Track win/loss statistics
- [ ] Implement opponent analysis

---

**Happy botting!** 🤖⚔️
