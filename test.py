import requests
import json

username = "tardigrade123"
BASE_URL = "https://api.splinterlands.io"

url = f"{BASE_URL}/cards/collection/{username}"
response = requests.get(url)

print("Status:", response.status_code)
print("Raw response:")
print(json.dumps(response.json(), indent=2))

