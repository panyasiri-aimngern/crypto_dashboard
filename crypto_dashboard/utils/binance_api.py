import requests
import time

BASE = "https://api.binance.com/api/v3"

def get_orderbook(symbol, limit=10):
    try:
        resp = requests.get(
            f"{BASE}/depth",
            params={"symbol": symbol, "limit": limit},
            timeout=5
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {"bids": [], "asks": []}

def get_klines(symbol, interval="1m", limit=60):
    try:
        resp = requests.get(
            f"{BASE}/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
            timeout=5
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []

def get_trades(symbol, limit=1000):
    try:
        resp = requests.get(
            f"{BASE}/trades",
            params={"symbol": symbol, "limit": limit},
            timeout=5
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []

def get_volume_ratio(symbol, minutes):
    trades = get_trades(symbol)
    now = time.time()

    buy = sell = 0.0
    for t in trades:
        trade_time = t.get("time", 0) / 1000
        if now - trade_time > minutes * 60:
            continue

        qty = float(t.get("qty", 0))
        if t.get("isBuyerMaker", False):
            sell += qty
        else:
            buy += qty

    return buy, sell # Return buy and sell volume over the last N minutes