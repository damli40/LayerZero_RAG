# rag/api_fetch/fetch_scan.py
import requests
import json
import os

def fetch_scan_messages(api_key: str, save_path: str = "data/layerzero_apis/scan_messages.json"):
    url = "https://api-mainnet.layerzeroscan.com/api/messages"
    headers = {"x-api-key": api_key}
    params = {
        "page": 1,
        "limit": 20,  # fetch more if needed
    }

    res = requests.get(url, headers=headers, params=params)
    data = res.json()

    with open(save_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Saved Scan API messages to {save_path}")
