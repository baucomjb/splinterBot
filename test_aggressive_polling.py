#!/usr/bin/env python3
"""
Aggressive polling test to catch battle detection window
"""
import time
import json
from splinterlands.api import client
import yaml

with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

username = config['account']['username']

print(f"Starting aggressive polling for {username}")
print("Polling every 200ms for 60 seconds...")
print("Go queue a battle NOW and watch for changes\n")
print("=" * 60)

# Get baseline
baseline = client.get_player_account(username)
baseline_battles = baseline.get('battles', 0)
baseline_wins = baseline.get('wins', 0)
baseline_keys = set(baseline.keys())

print(f"Baseline: {baseline_battles} battles, {baseline_wins} wins")
print(f"Fields: {len(baseline_keys)} total\n")

start_time = time.time()
poll_count = 0
changes_detected = []

try:
    while time.time() - start_time < 60:
        poll_count += 1
        
        data = client.get_player_account(username)
        current_battles = data.get('battles', 0)
        current_wins = data.get('wins', 0)
        
        # Check for any changes
        if current_battles != baseline_battles or current_wins != baseline_wins:
            elapsed = time.time() - start_time
            changes_detected.append({
                'time': elapsed,
                'battles': current_battles,
                'wins': current_wins,
                'delta_battles': current_battles - baseline_battles,
                'delta_wins': current_wins - baseline_wins,
            })
            print(f"\n⚠️  CHANGE DETECTED at {elapsed:.1f}s:")
            print(f"   Battles: {baseline_battles} → {current_battles}")
            print(f"   Wins: {baseline_wins} → {current_wins}")
            print(f"   Poll #{poll_count}\n")
        
        # Check for new keys or removed keys
        current_keys = set(data.keys())
        if current_keys != baseline_keys:
            new_keys = current_keys - baseline_keys
            removed_keys = baseline_keys - current_keys
            if new_keys:
                print(f"⚠️  New keys: {new_keys}")
            if removed_keys:
                print(f"⚠️  Removed keys: {removed_keys}")
        
        time.sleep(0.2)  # Poll every 200ms
        
        if poll_count % 25 == 0:
            print(f"Still polling... ({poll_count} checks, {time.time() - start_time:.1f}s elapsed)")

except KeyboardInterrupt:
    print("\n\nStopped by user")

elapsed = time.time() - start_time
print("\n" + "=" * 60)
print(f"Polling complete: {poll_count} polls in {elapsed:.1f}s")
print(f"Detected {len(changes_detected)} changes")

if changes_detected:
    print("\nChanges detected:")
    for change in changes_detected:
        print(f"  {change}")
else:
    print("\nNo changes detected during polling window")
