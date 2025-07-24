# rag/utils/summarize_wallet_messages.py

import json
from datetime import datetime

CHAIN_ID_MAP = {
    101: "Ethereum",
    102: "BSC",
    110: "Arbitrum",
    111: "Optimism",
    109: "Polygon",
    106: "Avalanche",
    # Add more as needed
}

def format_timestamp(timestamp):
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y %H:%M UTC")
    except Exception:
        return timestamp

def summarize_wallet_messages(data: dict, wallet: str):
    messages = data.get("items", [])
    summaries = []

    for msg in messages:
        src = CHAIN_ID_MAP.get(msg.get("srcChainId"), f"Chain {msg.get('srcChainId')}")
        dst = CHAIN_ID_MAP.get(msg.get("dstChainId"), f"Chain {msg.get('dstChainId')}")
        status = msg.get("status", "UNKNOWN")
        ts = format_timestamp(msg.get("timestamp", ""))
        tx_hash = msg.get("txHash", "")[:10] + "..." if msg.get("txHash") else "Unknown"

        summary = f"On {ts}, wallet {wallet} sent a message from {src} to {dst} (tx: {tx_hash}) — Status: {status}."
        summaries.append(summary)

    return summaries

# ---------------------------
# 👇 Run standalone
# ---------------------------
if __name__ == "__main__":
    wallet = "0x36599B0286D3c32F934BC8877eeA839D88f3AFFC"
    path = "data/layerzero_apis/wallet_messages.json"

    try:
        with open(path, "r") as f:
            data = json.load(f)

        summaries = summarize_wallet_messages(data, wallet)
        for s in summaries:
            print("🧠", s)

    except FileNotFoundError:
        print(f"❌ File not found: {path}")
    except Exception as e:
        print(f"❌ Error: {e}")
