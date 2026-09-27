#!/usr/bin/env python3
"""
Diagnostic: Check what the API returns when you have an active battle
Run this WHILE a battle is active to capture the response
"""
import json
import time
from splinterlands.api import client

username = "tardigrade123"

print(f"Checking {username}'s API response every 2 seconds...")
print("Queue a battle NOW and this script will show what changes.\n")
print("=" * 60)

baseline = None

try:
    while True:
        data = client.get_player_account(username)
        
        if baseline is None:
            baseline = data
            print("\n🔧 BASELINE (no active battle):")
            print(f"Keys: {list(data.keys())[:15]}")
        else:
            # Check for changes
            current_keys = set(data.keys())
            baseline_keys = set(baseline.keys())
            
            new_keys = current_keys - baseline_keys
            removed_keys = baseline_keys - current_keys
            
            # Check for value changes in common fields
            changed_values = {}
            for key in current_keys & baseline_keys:
                if data[key] != baseline[key]:
                    changed_values[key] = {
                        'before': baseline[key],
                        'after': data[key]
                    }
            
            if new_keys or removed_keys or changed_values:
                print(f"\n⚠️  CHANGE DETECTED!")
                
                if new_keys:
                    print(f"NEW FIELDS: {new_keys}")
                    for key in new_keys:
                        print(f"  {key}: {json.dumps(data[key], indent=2, default=str)[:100]}")
                
                if removed_keys:
                    print(f"REMOVED FIELDS: {removed_keys}")
                
                if changed_values:
                    print(f"CHANGED VALUES:")
                    for key, change in list(changed_values.items())[:5]:
                        print(f"  {key}:")
                        print(f"    before: {change['before']}")
                        print(f"    after:  {change['after']}")
                
                # Update baseline
                baseline = data
                print()
        
        time.sleep(2)

except KeyboardInterrupt:
    print("\n\nStopped by user")
    print("\nFinal response structure:")
    print(json.dumps(data, indent=2, default=str)[:500])
