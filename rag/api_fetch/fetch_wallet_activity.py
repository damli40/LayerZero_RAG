# rag/api_fetch/fetch_wallet_activity.py

import requests
import json
from datetime import datetime, timedelta
import os

def fetch_wallet_activity(wallet: str, days: int = 90, save_path="data/layerzero_apis/wallet_messages.json"):
    base_url = f"https://scan.layerzero-api.com/v1/messages/wallet/{wallet}"

    end = datetime.utcnow()
    start = end - timedelta(days=days)

    params = {
        "limit": 100,
        "start": start.isoformat() + "Z",
        "end": end.isoformat() + "Z"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Saved wallet activity for {wallet} to {save_path}")
        return data

    except Exception as e:
        print(f"❌ Failed to fetch wallet activity: {e}")
        return None
