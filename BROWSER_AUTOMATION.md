# Splinterlands Bot with Auto Battle Queuing

## 🎉 Discovery: API for Battle Queuing Exists!

You were right! Splinterlands bots CAN queue battles automatically. The public bots use **browser automation (Playwright/Puppeteer)** to click through the official Splinterlands web client UI.

This is the discovered "automated battling technique" - it's not a REST API endpoint, but rather **UI automation** that simulates user clicks on the Splinterlands website.

---

## ✨ What's New

Your bot now supports **three powerful modes**:

### 1. Single Run (Default)
```bash
python bot.py
```
- Detects if you have an active battle
- Submits team automatically
- Exits

### 2. Continuous Monitoring Mode ⚡
```bash
python bot.py --continuous [interval]
```
- Continuously checks for battles (every 3-30 seconds)
- Auto-submits teams as soon as a battle appears
- Runs 24/7 until stopped
- **NOTE:** Battles must be queued in Splinterlands client

**Best for:** Passive farming while running the client

### 3. **NEW** Auto Queue Mode 🤖
```bash
python bot.py --queue [interval]
```
- Uses **browser automation** to queue battles automatically
- Simultaneously submits teams
- Runs 24/7
- **Does NOT require manual queuing in Splinterlands client**

**Best for:** Fully automated 24/7 farming with zero manual interaction

---

## 🚀 How Auto Queue Works

### Architecture

```
Bot --[Playwright Browser]→ Splinterlands.com
        ↓
    [Hive Keychain Login]
        ↓
    [Click "BATTLE" button]
        ↓
    [Select "Ranked" → "Wild"]
        ↓
    [Click "FIND OPPONENT"]
        ↓
    [Opponent Found!]
        ↓
    [Auto-Submit Team via API]
        ↓
    [Battle Starts]
        ↓
    [Repeat]
```

The magic: **By using browser automation, the bot can queue battles just like you clicking the UI manually.**

---

## 📋 Requirements for Auto Queue

### 1. Hive Keychain Extension
- Install: [Chrome](https://chrome.google.com/webstore/detail/hive-keychain/jcacnejopjdphbnjgijlhicisredkcjl) | [Firefox](https://addons.mozilla.org/en-US/firefox/addon/hive-keychain/)
- This handles login automatically (no password needed!)
- Must be installed BEFORE using `--queue` mode

### 2. Browser Automation Dependencies
```bash
pip install playwright
python -m playwright install chromium
```

### 3. config.yaml
```yaml
account:
  username: "your_username"
  posting_key: "your_posting_key"

bot:
  mode: "wild"
  log_level: "info"
```

---

## 🎯 Quick Start

### Auto Queue (Fully Automatic)
```bash
# Simple - queue every 30 seconds
python bot.py --queue

# Or custom interval
python bot.py --queue 60
```

### Continuous (Manual Queue)
```bash
# Monitor and submit, you queue manually
python bot.py --continuous
```

---

## 📖 Full Documentation

See [BROWSER_AUTOMATION_DETAILED.md](BROWSER_AUTOMATION_DETAILED.md) for:
- Technical deep dive
- Troubleshooting
- Security considerations
- Performance tuning

---

**Your bot now has complete automated battling! 🎉**
