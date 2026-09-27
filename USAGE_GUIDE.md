# Splinterlands Wild Bot - Usage Guide

## 🤖 What This Bot Does

Your Splinterlands bot is an **automated team selection and farming tool**. It can:

✅ **Queue battles automatically** (new!)
✅ **Automatically select** an optimal Water splinter team
✅ **Instantly submit** the team to get into battle
✅ **Repeats infinitely** for 24/7 farming

## 🎯 Three Operating Modes

### Mode 1: Single Run (Default)
```bash
python bot.py
```
Detects one active battle, submits team, exits. Great for testing.

### Mode 2: Continuous Monitoring
```bash
python bot.py --continuous
```
You queue battles in Splinterlands client → Bot auto-submits teams → Repeats forever

### Mode 3: Full Auto Queue ⭐ **NEW**
```bash
python bot.py --queue
```
Bot queues battles automatically → Bot auto-submits teams → Repeats forever
No manual queuing needed!

---

## ⚡ Quick Start

### Option A: Full Automation (Recommended)
```bash
# Install dependencies
pip install playwright
python -m playwright install chromium

# Run auto queue mode
python bot.py --queue
```

This mode:
- ✅ Queues battles automatically via browser automation
- ✅ Submits teams instantly
- ✅ Requires Hive Keychain extension
- ✅ Zero manual interaction needed

## 🚀 Getting Started

### Step 1: Update Your Credentials

Edit `config/config.yaml`:
```yaml
account:
  username: "your_splinterlands_username"
  posting_key: "your_posting_key_from_hive_keychain"

bot:
  mode: "wild"
  log_level: "info"
```

### Step 2: Install Browser Automation (For Auto Queue)

```bash
pip install playwright
python -m playwright install chromium
```

### Step 3: Install Hive Keychain (For Auto Queue)

- **Chrome:** https://chrome.google.com/webstore/detail/hive-keychain/jcacnejopjdphbnjgijlhicisredkcjl
- **Firefox:** https://addons.mozilla.org/en-US/firefox/addon/hive-keychain/

### Step 4: Run the Bot

```bash
# Option A: Fully automatic (recommended)
python bot.py --queue

# Option B: Monitor and submit (you queue manually)
python bot.py --continuous

# Option C: Single test run
python bot.py
```

---

## 📋 Detailed Mode Descriptions

### Mode 1: Single Run (Default)

**Command:**
```bash
python bot.py
```

**What it does:**
1. Connects to your account
2. Checks for active battles
3. If battle found: Selects team and submits
4. If no battle: Shows account status and exits

**Use cases:**
- Testing setup
- Manual invocation
- Cron jobs that run periodically

**Example output:**
```
=== Account Summary for tardigrade123 ===
Rating: 2300
Record: 12743W - 10548L (54.7%)
Status: Waiting for battle...

⏳ No active battle. Waiting for battle matchmaking...
```

### Mode 2: Continuous Monitoring ⚡

**Command:**
```bash
python bot.py --continuous [interval]
```

**What it does:**
1. Continuously polls your account (every 3 seconds by default)
2. When a battle appears → Auto-submits team immediately
3. Waits for next battle
4. Repeats forever

**Parameters:**
- `[interval]` - Seconds between checks (default: 3, range: 1-60)

**Use cases:**
- Running while manually queueing battles
- Passive farming with manual control
- Testing team selection logic

**Workflow:**
```
1. Start bot: python bot.py --continuous
2. Open Splinterlands.com 
3. Queue battle ("Play" → "Ranked" → "Wild")
4. Bot detects within 1-3 seconds
5. Bot auto-submits team
6. Battle plays
7. Repeat steps 3-6 infinitely
```

**Example output:**
```
🤖 Splinterlands Wild Bot Starting
   Account: tardigrade123
   Mode: CONTINUOUS (checking every 3s)
   Waiting for battles...

⏳ No active battle. Checking again in 3s...
⏳ No active battle. Checking again in 3s...

🎯 BATTLE #1 DETECTED
⚔️ Active battle found!
🃏 Loading card pool...
   Total available cards: 247
🎯 Selecting team with Water Bot strategy...
📤 Submitting team to battle...
✅ Team submitted successfully!

⏳ No active battle. Checking again in 3s...
```

### Mode 3: Full Auto Queue 🤖 **NEW**

**Command:**
```bash
python bot.py --queue [interval]
```

**What it does:**
1. Launches browser automation
2. Logs in with Hive Keychain
3. **Clicks "BATTLE" button automatically**
4. **Selects Ranked → Wild automatically**
5. **Finds opponent automatically**
6. When opponent found → Auto-submits team
7. Battle plays
8. Repeats forever (every 30 seconds by default)

**Parameters:**
- `[interval]` - Seconds between queue attempts (default: 30, range: 10-300)

**Requirements:**
- Hive Keychain extension installed
- Playwright installed (`pip install playwright`)
- Chromium browser (`python -m playwright install chromium`)

**Use cases:**
- **24/7 fully automated farming**
- Hands-off operation
- Maximum farming efficiency
- No manual interaction needed

**Workflow:**
```
Loop:
  1. Bot launches chromium browser
  2. Bot navigates to splinterlands.com
  3. Bot logs in with Hive Keychain (automatic)
  4. Bot clicks BATTLE button
  5. Bot selects Ranked + Wild
  6. Bot clicks FIND OPPONENT
  7. Bot waits for opponent (~10-30 seconds)
  8. Opponent found!
  9. Bot auto-submits team via API
  10. Battle starts
  11. Wait 30 seconds
  12. Repeat
```

**Example output:**
```
🤖 Splinterlands Bot - AUTO QUEUE Mode
   Account: tardigrade123
   Check Interval: 30s

============================================================
🎮 Queue Attempt #1
============================================================
🌐 Launching browser to queue battle...
🔑 Attempting login with Hive Keychain...
✅ Hive Keychain login initiated
📌 Clicking BATTLE button...
✓ Selected Ranked mode
✓ Selected Wild format
🔍 Clicking FIND OPPONENT...
✅ Opponent found! Team selection dialog appeared
🃏 Selecting team...
📤 Submitting team to battle...
✅ Team submitted successfully!

============================================================
🎮 Queue Attempt #2
============================================================
[repeats...]
```

---

## 🔧 Advanced Configuration

### Custom Check Intervals

```bash
# Continuous mode - check more frequently for faster response
python bot.py --continuous 1    # Check every 1 second

# Auto queue - queue less frequently to reduce load
python bot.py --queue 60        # Queue every 60 seconds
```

### Multiple Accounts

Run separate instances with different config files:

```bash
# Account 1
CONFIG=config_account1.yaml python bot.py --queue

# Account 2  
CONFIG=config_account2.yaml python bot.py --queue
```

### Scheduled/Cron Execution

```bash
# Use continuous mode with timeout
timeout 3600 python bot.py --continuous  # Run for 1 hour

# Add to crontab
*/5 * * * * cd /home/user/splinterlands_bot && python bot.py  # Every 5 minutes
0 */2 * * * cd /home/user/splinterlands_bot && timeout 7200 python bot.py --continuous  # Every 2 hours for 2 hours
```

### Running as Background Service

```bash
# Using nohup
nohup python bot.py --queue > bot.log 2>&1 &

# Using screen
screen -d -m -S splinter python bot.py --queue

# Using systemd (see USAGE_GUIDE_SYSTEMD.md for full setup)
systemctl start splinter-bot
```

## 🔄 Typical Workflow

1. **Terminal 1 - Bot:**
   ```bash
   python bot.py --continuous
   ```
   Output:
   ```
   🤖 Splinterlands Wild Bot Starting
      Account: tardigrade123
      Mode: CONTINUOUS (checking every 3s)
      Waiting for battles...
   
   ⏳ No active battle. Checking again in 3s...
   ```

2. **Terminal 2 (or Web Browser) - Queue Battle:**
   - Open Splinterlands.com
   - Click "Play" → "Ranked" → "Wild"
   - Battle queues and matches

3. **Bot Auto-Submits:**
   ```
   ============================================================
   🎯 BATTLE #1 DETECTED
   ============================================================
   
   ⚔️ Active battle found! Starting team selection...
   Battle Summary: {...}
   
   🃏 Loading card pool...
      Total available cards: 247
   
   🎯 Selecting team with Water Bot strategy...
   Water Bot Selecting Team...
     Mana Cap: 45
     Rulesets: ['Melee Only']
     Allowed Splinters: ['Water', 'Fire']
     ✅ Selected Summoner: Kelya Frendul (Lvl 4)
     ✅ Selected 3 Monsters:
        1. Phantom Soldier (Lvl 3)
        2. Wave Runner (Lvl 2)
        3. Naga Fire Witch (Lvl 2)
   
   === Team Summary ===
   Battle ID: abc123def456...
   Splinter: Water
   Summoner: Kelya Frendul (Lvl 4)
   Monsters (3)
     1. Phantom Soldier (Lvl 3) - ...stats...
     2. Wave Runner (Lvl 2) - ...stats...
     3. Naga Fire Witch (Lvl 2) - ...stats...
   
   📤 Submitting team to battle...
   ✅ Team submitted successfully!
      Battle ID: abc123def456...
   
   ⏳ Waiting 3s before next check...
   ```

4. **Battle Plays Out:** 
   - Your team battles the opponent
   - Bot waits for next battle to queue

5. **Repeat:** Loop continues indefinitely

## 📊 Example Output

### Account Status
```
=== Account Summary for tardigrade123 ===
Rating: 2300
Record: 12743W - 10548L (54.7%)
Collection Power: 707410
League: 8
Status: Idle (waiting for battle)
```

### Team Selection Example
```
Water Bot Selecting Team...
  Mana Cap: 45
  Rulesets: ['Armor Up']
  Allowed Splinters: ['Water', 'Earth']
  ✅ Selected Summoner: Marjax Prinn (Lvl 3)
  ✅ Selected 4 Monsters:
     1. Silvershield Knight (Lvl 4)
     2. Caustic Sludge (Lvl 2)
     3. Peaceful Giant (Lvl 2)
     4. Naga Trainer (Lvl 1)
```

## ⚙️ Configuration Options

Edit `config/config.yaml`:

```yaml
account:
  username: "tardigrade123"
  posting_key: "your_hive_posting_key"

bot:
  mode: "wild"                    # Game mode
  log_level: "info"               # Logging level: debug, info, warning, error
```

### Log Levels Explained

- **debug** - Verbose output, every step
- **info** - Standard output, important events
- **warning** - Only warnings and errors
- **error** - Only errors

## 🎯 How the Bot Selects Teams

The bot uses the **Water Bot Strategy**:

1. **Filters** cards to Water splinter only (Blue color)
2. **Selects** highest-level Water summoner
3. **Restricts** based on battle rulesets:
   - Melee Only → Only melee attackers
   - Ranged Only → Only ranged/magic users
   - Magic Only → Only magic users
   - Lost Legendaries → Excludes rare cards
4. **Prioritizes** monsters by:
   - Survivability (health + armor)
   - Card level (strength)
   - Mana efficiency
5. **Stays within** mana cap (15-99 mana)
6. **Fills** up to 5 monster slots

## 🔍 Troubleshooting

### Bot Says "No Active Battle"

**Problem:** You're running single-run mode but battle takes time to queue

**Solution:** Use continuous mode:
```bash
python bot.py --continuous
```

### "Water splinter not allowed"

**Problem:** This battle doesn't allow Water cards

**Solution:** The bot checks this and skips the battle. Queue another one. (Future enhancement: multi-splinter support)

### "Invalid credentials" or "Signature error"

**Problem:** Wrong posting key in `config/config.yaml`

**Solution:** 
1. Get correct key from Hive Keychain or account
2. Update `config/config.yaml`
3. Restart bot

### Bot crashes with API error

**Problem:** Splinterlands API is temporarily down

**Solution:**
1. Check API status
2. Restart bot - it will retry
3. In continuous mode, it keeps trying

### Card pool is empty / "No water cards"

**Problem:** All your water cards are on sale, delegated, or rented

**Solution:**
1. Undelegated/unrent water cards
2. Remove from marketplace
3. Restart bot

## 📈 Performance Tips

### For Faster Response

```bash
python bot.py --continuous 1   # Check every 1 second
```

### For Lower API Load

```bash
python bot.py --continuous 10  # Check every 10 seconds
```

### For Production

Run with a process manager that auto-restarts on crash:

```bash
# Using nohup
nohup python bot.py --continuous &

# Or using screen
screen -d -m -S splinter python bot.py --continuous

# Or using systemd (advanced)
# Create /etc/systemd/system/splinter-bot.service
[Unit]
Description=Splinterlands Bot
After=network.target

[Service]
Type=simple
User=jbaucom
WorkingDirectory=/home/jbaucom/code/splinterlands_bot
ExecStart=/usr/bin/python3 bot.py --continuous
Restart=always

[Install]
WantedBy=multi-user.target

# Then:
sudo systemctl start splinter-bot
sudo systemctl status splinter-bot
```

## 🛡️ Security Notes

- **Never commit** `config/config.yaml` to git (add to `.gitignore`)
- Your **posting key is sensitive** - it can transact on your account
- Only use **trusted** instances of this code
- The bot uses **HMAC-SHA256 signing** (industry standard)

## 🎓 What Endpoints Are Used

**Read-Only:**
- `GET /players/details` - Account info
- `GET /cards/collection/{username}` - Your cards
- `GET /cards/get_details` - Card metadata  
- `GET /players/outstanding_match` - Check for active battles
- `GET /battle/battle_queue` - View queued battles

**Write (requires key signing):**
- `POST /battle/submit_team` - Submit team (signed with posting key)

## 📚 Next Steps

1. **Test the bot** - Run once with `python bot.py`
2. **Queue a battle** manually in Splinterlands client
3. **Run continuous mode** - `python bot.py --continuous`
4. **Monitor battles** - Watch your account get auto-submitted teams!

## 🚀 Future Enhancements

See [EXTENDING.md](EXTENDING.md) for how to add:
- Multi-splinter strategies (Fire, Earth, Life, Death, Dragon)
- Opponent analysis
- ML-based win prediction
- Battle statistics tracking
- Advanced scheduling

---

**Happy botting!** Questions? Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) or [ARCHITECTURE.md](ARCHITECTURE.md)
