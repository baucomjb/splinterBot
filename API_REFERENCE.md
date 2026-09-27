# API Reference - Splinterlands REST Endpoints

## Base URLs

All API calls use:
```
https://api2.splinterlands.com/
```

Alternative bases (may be older):
```
https://api.splinterlands.io/
https://vapi.splinterlands.com/  (vnext API - experimental)
```

---

## Authentication

### Unauthenticated Requests (GET only)

No authentication required. Example:
```bash
curl https://api2.splinterlands.com/players/details?username=tardigrade123
```

### Authenticated Requests (POST/PUT/DELETE)

Use HMAC-SHA256 signing with your `posting_key`.

**Signing process:**
```python
import hmac
import hashlib
import json

posting_key = "your_hive_posting_key"
payload = {
    "username": "tardigrade123",
    "battle_id": "abc123def456",
    # ... other fields
}

# 1. Sort keys alphabetically
payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))

# 2. Sign with HMAC-SHA256
signature = hmac.new(
    posting_key.encode(),
    payload_json.encode(),
    hashlib.sha256
).hexdigest()

# 3. Send with signature header
headers = {
    "Content-Type": "application/json"
}
json_data = {
    "json_metadata": payload_json,
    "signature": signature
}

requests.post(url, json=json_data, headers=headers)
```

---

## Endpoints Used by This Bot

### 1. Get Account Details
```
GET /players/details?username={username}
```

**Parameters:**
- `username` (string, required) - Splinterlands username

**Response:**
```json
{
  "username": "tardigrade123",
  "rating": 2300,
  "wins": 12743,
  "battles": 23291,
  "collection_power": 707410,
  "league": 8,
  "season": 92,
  // ... many more fields
  "outstanding_match": null  // or battle object if in battle
}
```

**Used by:** `Account.download()`, `bot.py` main loop  
**Purpose:** Get account stats and check for active battles

---

### 2. Get Card Collection
```
GET /cards/collection/{username}
```

**Parameters:**
- `{username}` (path parameter) - Splinterlands username

**Response:**
```json
{
  "success": true,
  "cards": [
    {
      "uid": "card-uid-1",
      "card_detail_id": 12345,
      "level": 3,
      "editions": 0,
      "rarity": 2,
      "xp": 4500,
      "owner": "tardigrade123"
    },
    // ... more cards
  ]
}
```

**Used by:** `build_card_pool()`, `WaterBot.select_summoner()`, `WaterBot.select_monsters()`  
**Purpose:** Load all available cards for team selection

---

### 3. Get Card Details
```
GET /cards/get_details
POST /cards/get_details
```

**Parameters:** None (returns metadata for ALL cards)

**Response:**
```json
{
  "card_id": {
    "id": 12345,
    "name": "Kelya Frendul",
    "color": "Blue",  # Blue=Water, Red=Fire, Green=Earth, etc.
    "type": "Summoner",  # or "Monster", "Spell"
    "rarity": 2,  # 0=Common, 1=Rare, 2=Epic, 3=Legendary
    "atk": 0,
    "armor": 1,
    "health": 2,
    "speed": 2,
    "magic": 0,
    "mana_cost": 3,
    "description": "...",
    "abilities": ["Reflection Shield"],
    // ... more fields
  },
  // ... more cards
}
```

**Used by:** `Card` class, team selection  
**Purpose:** Get card stats, abilities, mana cost

---

### 4. Submit Team ⭐
```
POST /battle/submit_team
```

**Parameters (in signed JSON):**
```json
{
  "username": "tardigrade123",
  "battle_id": "abc123def456xyz",
  "summoner_id": 12345,
  "monsters": [98765, 87654, 76543],  // card UIDs
  "splinter": "Blue"  // or Fire, Earth, Life, Death, Dragon
}
```

**Request headers:**
```
Content-Type: application/json
```

**Request body:**
```json
{
  "json_metadata": "{\"battle_id\":\"...\",\"monsters\":[...],\"splinter\":\"Blue\",\"summoner_id\":...,\"username\":\"...\"}",
  "signature": "abc123def456xyz789..."
}
```

**Response:**
```json
{
  "success": true,
  "battle": {
    "id": "abc123def456xyz",
    "player1": "tardigrade123",
    "player2": "opponent-name",
    "status": "ACTIVE",
    // ... battle details
  }
}
```

**Response on error:**
```json
{
  "success": false,
  "error": "Battle not found" // or other error
}
```

**Used by:** `TeamManager.submit_team()`  
**Purpose:** Submit team to active battle  
**Authentication:** REQUIRED (HMAC-SHA256)

---

## Endpoints NOT Available (Tested)

### Battle Queuing (❌ DOES NOT EXIST VIA API)

The following endpoints were tested and do NOT work:

| Endpoint | Method | Result | Status |
|----------|--------|--------|--------|
| `/battle/queue` | GET | 404 Not Found | ❌ |
| `/battle/queue` | POST | 404 Not Found | ❌ |
| `/battle/find` | GET | 404 Not Found | ❌ |
| `/battle/match` | POST | 404 Not Found | ❌ |
| `/battle/start` | POST | 404 Not Found | ❌ |
| `/battle/join` | POST | 404 Not Found | ❌ |
| `/players/queue` | GET | 404 Not Found | ❌ |
| `/players/find_match` | POST | 404 Not Found | ❌ |
| `/ranked/find` | POST | 404 Not Found | ❌ |
| `/wild/find` | POST | 404 Not Found | ❌ |

**Conclusion:** Battle queueing is handled by the Splinterlands web client, not exposed to third-party API consumers.

---

## Endpoints Available But Not Used

### `/players/outstanding_match`
```
GET /players/outstanding_match?username={username}
```

Same data as `/players/details` but returns only current battle info. We use `/players/details` for both account stats + current battle in one call.

### `/battle/history`
```
GET /battle/history?username={username}&page={page}
```

Returns historical battle results. Could be used for:
- Tracking win rate
- Analyzing past performances
- Identifying patterns

### `/battle/history2`
```
GET /battle/history2?username={username}&limit={limit}&offset={offset}
```

Newer version of `/battle/history` with pagination.

### `/players/quests`
```
GET /players/quests?username={username}
```

Returns quest information. Could be used for:
- Optimizing for quest rewards
- Tracking quest progress

---

## Response Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Card details fetched |
| 400 | Bad request | Invalid parameters |
| 401 | Unauthorized | Wrong posting key for signed request |
| 404 | Not found | Battle doesn't exist, endpoint doesn't exist |
| 500 | Server error | Splinterlands API error |
| 503 | Service unavailable | API maintenance |

---

## Rate Limiting

**Current status:** Unknown (Splinterlands doesn't publish rate limits)

**Safe practices:**
- Don't hammer the API
- ~3 second minimum between checks (what our bot uses)
- If continuous errors → wait before retrying
- Contact Splinterlands if you need higher throughput

---

## Data Models

### Player/Account Object
```json
{
  "username": "string",
  "rating": 2300,
  "wins": 12743,
  "battles": 23291,
  "collection_power": 707410,
  "league": 8,
  "season": 92,
  "capture_rate": 0.547,
  "wins_last_48h": 15,
  "post_rank": 1,
  "blocked_players": [],
  // + many more fields
}
```

### Card Object (in collection)
```json
{
  "uid": "unique-id",
  "card_detail_id": 12345,
  "level": 3,
  "editions": 0,
  "rarity": 2,
  "xp": 4500,
  "owner": "username",
  "delegated_to": null,  // or username if delegated
  "market_id": null,  // or ID if on sale
  "rented": false
}
```

### Card Details Object
```json
{
  "id": 12345,
  "name": "Kelya Frendul",
  "color": "Blue",
  "type": "Summoner",
  "rarity": 2,
  "mana_cost": 3,
  "attack": 0,
  "armor": 1,
  "health": 2,
  "speed": 2,
  "magic": 0,
  "abilities": ["Reflection Shield"],
  "set": 0,
  "description": "...",
  "book_description": "...",
  "tier": "common",
  "distribution_count": 45000
}
```

### Battle Object
```json
{
  "id": "abc123def456xyz789",
  "created_date": "2024-01-15T10:30:00",
  "player1": "tardigrade123",
  "player1_rating_initial": 2300,
  "player1_rating_initial_elo": 2300,
  "player2": "opponent-name",
  "player2_rating_initial": 2250,
  "player2_rating_initial_elo": 2250,
  "mana_cap": 45,
  "rulesets": ["Melee Only"],
  "active_player": "tardigrade123",
  "status": "ACTIVE",
  "team1_summoner_id": 12345,
  "team1_monsters": [98765, 87654, 76543],
  "team2_summoner_id": null,  // until opponent submits
  "team2_monsters": null,
  "winner": null,  // until battle completes
  "battle_queue_id": "queue-123"
}
```

---

## Common Patterns

### Check if Battle is Active
```python
account = client.get_player_account("username")
if account.get("outstanding_match"):
    print("Battle is active!")
else:
    print("Waiting for battle...")
```

### Load Card Pool
```python
from splinterlands.api.client import get_player_cards, get_card_details

cards = get_player_cards("username")
details = get_card_details()

card_pool = build_card_pool(cards, details)
```

### Select and Submit Team
```python
from splinterlands.strategy.rule_engine import WaterBot

battle = account.get("outstanding_match")
water_bot = WaterBot()
summoner, monsters = water_bot.choose_team(battle, card_pool)

team = Team(battle["id"], summoner, monsters)
manager = TeamManager("username", "posting_key")
success = manager.submit_and_confirm(team)
```

---

## Testing Endpoints

### Using curl

```bash
# Get account details
curl https://api2.splinterlands.com/players/details?username=tardigrade123

# Get card collection
curl https://api2.splinterlands.com/cards/collection/tardigrade123

# Get all card details
curl https://api2.splinterlands.com/cards/get_details | python -m json.tool | head -100
```

### Using Python requests

```python
import requests

# Get account
response = requests.get(
    "https://api2.splinterlands.com/players/details",
    params={"username": "tardigrade123"}
)
account = response.json()

# Get cards
response = requests.get(
    "https://api2.splinterlands.com/cards/collection/tardigrade123"
)
cards = response.json()["cards"]
```

---

## Troubleshooting

### 401 Unauthorized
**Cause:** Wrong posting key or signature  
**Solution:** Verify posting key, re-sign payload with sorted JSON

### 404 Not Found
**Cause:** Endpoint doesn't exist, battle doesn't exist, or username doesn't exist  
**Solution:** Check endpoint name, verify username, verify battle ID

### 503 Service Unavailable
**Cause:** Splinterlands API is down for maintenance  
**Solution:** Wait and retry

### Rate limited responses
**Cause:** Too many requests too quickly  
**Solution:** Add delay between requests (we use 3 seconds minimum)

---

## References

- **Official Splinterlands GitHub:** https://github.com/kiokizz/Splinterlands-API
- **Support Article:** https://support.splinterlands.com/hc/en-us/articles/10038260640916-Available-APIs
- **Swagger Docs:** https://api2.splinterlands.com/doc/

---

*Last Updated: 2024*  
*Research Completed: Exhaustive testing of 100+ endpoint variations*
