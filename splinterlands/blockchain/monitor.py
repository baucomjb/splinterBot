"""
Monitor Hive blockchain for Splinterlands battle challenge events.

When a battle is matched, Splinterlands creates a 'challenge' operation
on the Hive blockchain. We monitor for this to detect battles without
needing REST API or browser automation.
"""

import requests
import logging
import time
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

HIVE_RPC_URL = "https://api.hive.blog"  # Public Hive API endpoint


def get_account_history(username: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch recent operations for an account from Hive blockchain.
    
    Args:
        username: Splinterlands username
        limit: Number of recent operations to fetch
        
    Returns:
        List of operations (transaction history)
    """
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "condenser_api.get_account_history",
            "params": [username, -1, limit],
            "id": 1,
        }
        
        response = requests.post(HIVE_RPC_URL, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if "error" in data:
            logger.error(f"Hive RPC error: {data['error']}")
            return []
        
        # Result is list of [index, operation_dict]
        operations = []
        if "result" in data:
            for item in data["result"]:
                if isinstance(item, list) and len(item) >= 2:
                    operations.append(item[1])
        
        return operations
        
    except Exception as e:
        logger.error(f"Failed to fetch account history: {e}")
        return []


def find_challenges(username: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Find all recent 'challenge' operations for an account.
    Each challenge = battle was matched.
    
    Args:
        username: Splinterlands username
        limit: Number of recent operations to search
        
    Returns:
        List of challenge operations
    """
    operations = get_account_history(username, limit=limit)
    challenges = []
    
    for op in operations:
        if isinstance(op, dict):
            # Operations are structured as: {"op": [type, { data }], ...}
            op_array = op.get("op", [])
            
            if isinstance(op_array, list) and len(op_array) >= 2:
                op_type = op_array[0]  # e.g., "custom_json"
                op_data = op_array[1]  # e.g., {"id": "sm_challenge", ...}
                
                # Look for Splinterlands challenge operations
                if op_type == "custom_json":
                    if op_data.get("id") == "sm_challenge":
                        challenges.append(op)
    
    return challenges


def has_new_challenge(username: str, last_block: Optional[int] = None) -> bool:
    """
    Check if there's a new challenge (battle) since we last checked.
    
    Args:
        username: Splinterlands username
        last_block: Last block number we saw (for filtering)
        
    Returns:
        True if new challenge found, False otherwise
    """
    challenges = find_challenges(username, limit=20)
    
    if not challenges:
        return False
    
    # Get most recent challenge
    latest = challenges[0]
    
    # If this is a new challenge we haven't seen before
    if last_block is None or latest.get("block_num", 0) > last_block:
        return True
    
    return False


def monitor_for_battles(username: str, check_interval: int = 3) -> Dict[str, Any]:
    """
    Monitor blockchain for a single new challenge (battle).
    Blocks until one is found.
    
    Args:
        username: Splinterlands username
        check_interval: Seconds between checks
        
    Returns:
        Challenge operation data
    """
    logger.info(f"👁️  Monitoring blockchain for {username}'s battle matches...")
    logger.info(f"   Checking every {check_interval}s for new 'sm_challenge' operations")
    
    last_block = None
    check_count = 0
    
    while True:
        try:
            challenges = find_challenges(username, limit=20)
            
            if challenges:
                latest = challenges[0]
                current_block = latest.get("block_num", 0)
                
                if last_block is None:
                    logger.info(f"   Baseline: block #{current_block}, {len(challenges)} recent challenge(s)")
                    last_block = current_block
                elif current_block > last_block:
                    logger.info(f"✅ NEW BATTLE DETECTED!")
                    logger.info(f"   Block #{current_block} (previous: #{last_block})")
                    return latest
                else:
                    check_count += 1
                    if check_count % 5 == 0:
                        logger.debug(f"Still monitoring... (checked {check_count} times)")
            
            time.sleep(check_interval)
            check_count += 1
            
        except Exception as e:
            logger.error(f"⚠️  Check error: {e}")
            time.sleep(check_interval)


def get_last_challenge_block(username: str) -> Optional[int]:
    """
    Get the block number of the most recent challenge.
    
    Args:
        username: Splinterlands username
        
    Returns:
        Block number or None if no challenges found
    """
    challenges = find_challenges(username, limit=1)
    if challenges:
        return challenges[0].get("block_num")
    return None


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    username = sys.argv[1] if len(sys.argv) > 1 else "tardigrade123"
    
    print(f"\nMonitoring {username} for battle challenges...\n")
    challenge = monitor_for_battles(username)
    print(f"\n✅ Battle found!")
    print(f"Block: {challenge.get('block_num')}")
