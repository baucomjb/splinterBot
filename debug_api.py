#!/usr/bin/env python3
"""
Debug script to check API responses for battle detection
"""
import json
from splinterlands.api import client

username = "tardigrade123"

print(f"Checking battle status for {username}\n")

# Get player details
print("=" * 60)
print("GET /players/details")
print("=" * 60)
data = client.get_current_battle(username)
print(json.dumps(data, indent=2, default=str))

# Check specific fields
print("\n" + "=" * 60)
print("BATTLE DETECTION ANALYSIS")
print("=" * 60)
print(f"'battle' field present: {'battle' in data}")
print(f"'status' field present: {'status' in data}")

# List ALL top-level keys
print(f"\nAll top-level keys in response:")
for key in sorted(data.keys()):
    value = data[key]
    if isinstance(value, (dict, list)):
        print(f"  {key}: {type(value).__name__} (not shown for brevity)")
    else:
        print(f"  {key}: {value}")

# Check if there are queued battles
if 'queued_battles' in data:
    print(f"\n⚠️  Found 'queued_battles': {data['queued_battles']}")
if 'battle_queue' in data:
    print(f"\n⚠️  Found 'battle_queue': {data['battle_queue']}")
