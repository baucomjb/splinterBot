# Bot Architecture Overview

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     MAIN BOT LOOP (bot.py)                       │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ├─→ Load Config ──→ config/config.yaml
           │
           ├─→ Download Account Data
           │   └─→ Account class queries:
           │       ├─ get_player_account()     → Player stats
           │       ├─ get_player_quests()      → Active quest
           │       └─ get_current_battle()     → Battle status
           │
           ├─→ Has Active Battle?
           │   └─→ NO: Exit, wait for matchmaking
           │   └─→ YES: Continue...
           │
           ├─→ Parse Battle State
           │   └─ BattleState class extracts:
           │       ├─ Battle ID
           │       ├─ Mana Cap
           │       ├─ Rulesets
           │       └─ Allowed Splinters
           │
           ├─→ Build Card Pool
           │   └─ build_card_pool() queries:
           │       ├─ get_player_cards()        → Your collection
           │       └─ get_card_details()        → Card stats/abilities
           │       → Returns List[Card] with full game stats
           │
           ├─→ Select Team
           │   └─ choose_team() uses WaterBot:
           │       ├─ Filter to Water cards only
           │       ├─ Select best Summoner
           │       ├─ Select Monster composition
           │       │   ├─ Respect mana cap
           │       │   ├─ Apply ruleset filters
           │       │   └─ Prioritize by stats/level
           │       └─ Return (Summoner, [Monsters])
           │
           ├─→ Create Team Object
           │   └─ Team class:
           │       ├─ Stores: battle_id, summoner, monsters
           │       ├─ Determines splinter color
           │       └─ Formats for API submission
           │
           └─→ Submit Team
               └─ TeamManager.submit_and_confirm():
                   ├─ Sign request with HMAC-SHA256
                   └─ POST to /battle/submit_team
                   └─ Confirm success or show error
```

## Module Dependencies

```
bot.py (main)
├── config/config.yaml
└── Imports:
    ├── Account (game/account.py)
    │   └── Imports: api/client.py
    │
    ├── build_card_pool (game/card_pool.py)
    │   ├── Imports: api/cards.py
    │   ├── Imports: Card (game/card.py)
    │   └── Imports: Stats (game/stats.py)
    │
    ├── BattleState (game/battle_state.py)
    │
    ├── TeamManager (game/team.py)
    │   ├── Imports: Team (game/team.py)
    │   └── Imports: api/client.py
    │
    └── choose_team (strategy/rule_engine.py)
        ├── Imports: WaterBot strategy
        └── Imports: Card (game/card.py)

API Layer (api/):
├── client.py
│   ├── get_player_account()
│   ├── get_player_quests()
│   ├── get_current_battle()
│   ├── submit_team()
│   └── BASE_URL = https://api2.splinterlands.com
│
└── cards.py
    ├── get_player_cards()
    └── get_card_details()
```

## Data Flow: From API to Team Submission

```
1. ACCOUNT DATA
   ┌─────────────────────────────────────────┐
   │ API Response: get_player_account()       │
   │ {dec_balance, rating, season_wins, ...}  │
   └──────────────→ Account object
                    │ .get_dec_balance()
                    │ .get_rating()
                    │ .get_season_info()
                    │ .summary()

2. CARD POOL
   ┌──────────────────────────────────────┐
   │ get_player_cards() → List of owned   │
   │ get_card_details() → Static metadata │
   └──────────────→ build_card_pool()
                    │
                    ├─ Merge player cards with details
                    ├─ Extract stats for each level
                    ├─ Parse abilities
                    └─ Create Card objects
                    │
                    └─ List[Card] with:
                       ├─ name, type, color (splinter)
                       ├─ rarity, level, edition
                       ├─ stats (melee, magic, ranged, armor, health, speed)
                       ├─ abilities list
                       └─ status flags (on_land, for_sale, delegated, rented)

3. BATTLE STATE
   ┌──────────────────────────────────────┐
   │ get_current_battle() API response     │
   │ {battle: {id, mana_cap, ruleset, ...}} │
   └──────────────→ BattleState object
                    │
                    ├─ Extracts battle_id
                    ├─ Parses mana_cap
                    ├─ Splits rulesets string
                    ├─ Calculates allowed_splinters
                    └─ Stores opponent info

4. TEAM SELECTION
   ┌───────────────────────────────────┐
   │ choose_team(battle_state, cards)   │
   │ Uses: WaterBot strategy            │
   └────────────→ WaterBot algorithm
                  │
                  ├─ Filter to Blue cards
                  ├─ Select highest-level Summoner
                  ├─ Apply ruleset filters
                  ├─ Select monsters by stats
                  └─ Respect mana constraints
                  │
                  └─ (Summoner, [Monster1, Monster2, ...])

5. TEAM SUBMISSION
   ┌──────────────────────────────┐
   │ Team object construction     │
   │ {battle_id, summoner, monsters}
   └────────────→ Team.to_submission_dict()
                  │ Convert to:
                  │ {
                  │   "battle_id": "...",
                  │   "summoner_id": "uid",
                  │   "monsters": ["uid1", "uid2", ...],
                  │   "splinter": "Water"
                  │ }
                  │
                  └─→ HMAC-SHA256 SIGN with posting_key
                      │
                      └─→ POST /battle/submit_team
                          │
                          └─→ API Response: {success: true}
```

## Water Bot Strategy Details

```
WaterBot Class
├─ WATER_SUMMONERS: Set of summoner names
├─ WATER_CARDS: Dict of allowed monster names
│
└─ Methods:
   ├─ filter_water_cards(pool)
   │  └─ Keep only: type=="Summoner" AND name in WATER_SUMMONERS
   │              OR color=="Blue"
   │
   ├─ select_summoner(available)
   │  └─ max(by level) → Preferred summoner for team
   │
   ├─ select_monsters(available, mana_cap, rulesets)
   │  ├─ Apply ruleset filters (Melee Only, Ranged Only, etc.)
   │  ├─ Sort by: defense (health+armor), then by level
   │  ├─ Greedily fill mana budget
   │  └─ Return up to 5 monster cards
   │
   ├─ _apply_ruleset_filters(cards, rulesets)
   │  ├─ Melee Only → Keep only melee attack > 0
   │  ├─ Ranged Only → Keep only ranged+magic > 0
   │  ├─ Magic Only → Keep only magic > 0
   │  └─ Lost Legendaries → Exclude rarity==4
   │
   └─ _estimate_mana_cost(card)
      └─ Approximation: (rarity+1) * (level//2 + 1)
         [Note: Use actual costs from API for better accuracy]
```

## Class Relationships

```
Account
├─ Attributes: username, profile, quests, battle_data
├─ Methods: download(), get_dec_balance(), get_rating(), ...
└─ Purpose: Central hub for player account data

BattleState
├─ Attributes: battle_id, mana_cap, rulesets, allowed_splinters
├─ Methods: summary(), _parse_rulesets(), _parse_splinters()
└─ Purpose: Parse and store current battle conditions

Card
├─ Attributes: uid, name, type, color, stats, abilities, ...
├─ Methods: summary()
└─ Purpose: Individual card representation

Team
├─ Attributes: battle_id, summoner (Card), monsters (List[Card])
├─ Methods: to_submission_dict(), summary()
└─ Purpose: Represents selected team composition

TeamManager
├─ Attributes: username, posting_key
├─ Methods: create_team(), submit_team(), submit_and_confirm()
└─ Purpose: Handles team lifecycle (creation → submission)

WaterBot (Strategy)
├─ Class Methods: (all static)
├─ Methods: filter_water_cards(), select_summoner(), select_monsters(), ...
└─ Purpose: Card selection algorithm for Water splinter
```

## Security Notes

```
Authentication Flow:
1. Load posting_key from config/config.yaml
2. Create JSON payload with team data
3. HMAC-SHA256(posting_key, JSON_payload)
4. Add signature to payload
5. POST to /battle/submit_team

⚠️  Key Security Practices:
- Never commit config.yaml to git (.gitignore it!)
- Posting key = write permissions on your account
- Requests include timeout (10s) to prevent hanging
- API uses HTTPS for all endpoints
```

## Error Handling

```
Bot Exit Points:
├─ No active battle → Wait mode (returns)
├─ Battle parse fails → Log error, exit
├─ No card pool → Log error, exit
├─ Team selection fails → Log error, exit
├─ Team submission fails → Log error, show message
└─ Exception caught → Stack trace logged

All errors are caught and logged for debugging
```
