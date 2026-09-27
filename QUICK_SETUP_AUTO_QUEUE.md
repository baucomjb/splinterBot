# ⚡ Quick Setup for Auto Queue Mode

## 5 Minute Setup

### Step 1: Install Dependencies (1 min)
```bash
cd /home/jbaucom/code/splinterlands_bot
pip install playwright
python -m playwright install chromium
```

### Step 2: Install Hive Keychain Extension (2 min)
- **Chrome:** https://chrome.google.com/webstore/detail/hive-keychain/jcacnejopjdphbnjgijlhicisredkcjl
- **Firefox:** https://addons.mozilla.org/en-US/firefox/addon/hive-keychain/

Just click "Add to Chrome/Firefox" and confirm.

### Step 3: Verify Configuration (1 min)
```bash
cat config/config.yaml
```

Check:
```yaml
account:
  username: tardigrade123           # Your username
  posting_key: your_posting_key_here # Your posting key
```

### Step 4: Run! (1 min)
```bash
python bot.py --queue
```

**That's it!** Bot will now automatically queue battles 24/7.

---

## What You'll See

```
🤖 Splinterlands Bot - AUTO QUEUE Mode
   Account: tardigrade123
   Check Interval: 30s
⚠️  AUTO QUEUE MODE REQUIRES:
   - Hive Keychain browser extension installed
   - Browser will be automated with Playwright
   - Battles will be queued automatically

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
   Water Bot Selecting Team...
     Mana Cap: 45
     Rulesets: ['Melee Only']
📤 Submitting team...
✅ Team submitted successfully!

⏳ Waiting 30s before next queue attempt...
```

---

## Modes Comparison

```
python bot.py                    # Single test - manual everything
python bot.py --continuous       # Monitor mode - you queue, bot submits
python bot.py --queue            # ⭐ Full auto - everything automated
```

---

## Options

```bash
python bot.py --queue            # Default: queue every 30 seconds
python bot.py --queue 60         # Queue every 60 seconds
python bot.py --queue 10         # Aggressive: queue every 10 seconds
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Keychain button not found" | Install extension, refresh browser |
| "Failed to queue" | Check internet, increase interval (--queue 60) |
| "Cannot submit team" | Verify posting_key in config.yaml |
| Browser doesn't close | Kill with Ctrl+C, retry |

---

## Next Steps

- 📖 Read [DISCOVERY_SUMMARY.md](DISCOVERY_SUMMARY.md) - How this works
- 📚 Read [BROWSER_AUTOMATION.md](BROWSER_AUTOMATION.md) - Detailed guide
- 🔧 Read [USAGE_GUIDE.md](USAGE_GUIDE.md) - All features explained

---

**Ready? Run `python bot.py --queue` and start farming!** 🚀
