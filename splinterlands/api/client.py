import requests
import json
import hashlib
import hmac
from typing import List, Dict

BASE_URL = "https://api2.splinterlands.com"

def get_current_battle(username: str):
    """Get current player status and active battle if any"""
    url = f"{BASE_URL}/players/details"
    params = {"name": username}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_outstanding_battle(username: str, posting_key: str):
    """
    Get outstanding/active battle for a player (requires authentication).
    This is the correct endpoint to detect active battles.
    
    Args:
        username: Player username
        posting_key: Private key for signing
        
    Returns:
        Dict with active battle info, or null if no active battle
    """
    url = f"{BASE_URL}/players/outstanding_match"
    
    # Try with signature in params (GET request)
    payload = {"username": username}
    payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    signature = hmac.new(
        posting_key.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Try both GET and POST approaches
    try:
        # Try POST first (body signing)
        payload["signature"] = signature
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 404:
            # Try GET with params
            resp = requests.get(url, params={"username": username, "signature": signature}, timeout=10)
    except:
        # Fallback to GET
        resp = requests.get(url, params={"username": username, "signature": signature}, timeout=10)
    
    resp.raise_for_status()
    return resp.json()

def get_battle_details(battle_id: str):
    """Get detailed results of a specific battle"""
    url = f"{BASE_URL}/battle/result"
    params = {"id": battle_id}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_player_account(username: str) -> Dict:
    """Get account details including rating, wins, battles, season info"""
    # Using /players/details which has all account data
    url = f"{BASE_URL}/players/details"
    params = {"name": username}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def submit_team(username: str, posting_key: str, team_data: Dict) -> Dict:
    """
    Submit a selected team for battle.
    
    Args:
        username: Player username
        posting_key: Private key for signing (from config)
        team_data: Dict containing battle_id, summoner_id, monsters (list of card UIDs)
    
    Returns:
        API response with team confirmation
    """
    url = f"{BASE_URL}/battle/submit_team"
    
    # Prepare payload
    payload = {
        "username": username,
        "battle_id": team_data["battle_id"],
        "summoner_id": team_data["summoner_id"],
        "monsters": team_data["monsters"],  # List of card UIDs
        "splinter": team_data.get("splinter", ""),
    }
    
    # Sign the request using HMAC-SHA256
    payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    signature = hmac.new(
        posting_key.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    
    payload["signature"] = signature
    
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()

