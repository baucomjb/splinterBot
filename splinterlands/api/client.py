import requests

BASE_URL = "https://api2.splinterlands.com"

def get_current_battle(username: str):
    url = f"{BASE_URL}/players/details"
    params = {"name": username}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_battle_details(battle_id: str):
    url = f"{BASE_URL}/battle/result"
    params = {"id": battle_id}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

