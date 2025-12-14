import tkinter as tk
import threading
import websocket
import json
import requests
import time
import os
import webbrowser

from utils.binance_api import get_volume_ratio
from config import *
from components.orderbook import OrderBookPanel
from components.price_panels import BigPricePanel, TradesPanel, BestPricePanel
from components.technical import (
    CandlestickChart,
    VolumeRatioPanel,
    Volume24hPanel
)

# -----------------------------
# Dashboard App
# -----------------------------
class CryptoDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Dashboard")
        self.root.geometry("1200x720")
        self.root.configure(bg=BG)

        self.current_symbol = "BTCUSDT"
        self.price_ws = None
        self.is_closing = False

        # Panel visibility states
        self.show_volume = tk.BooleanVar(value=True)
        self.show_orderbook = tk.BooleanVar(value=True)
        self.show_trades = tk.BooleanVar(value=True)

        self.last_5m_price = None
        self.last_5m_fetch = 0

        self.load_preferences()
        self.build_header()
        self.build_main()

        self.start_price_stream()
        self.trades_panel.start(self.current_symbol)
        self.orderbook.load(self.current_symbol)
        self.chart.load(self.current_symbol)

        # Load initial volumes in background
        threading.Thread(target=self._load_volumes, daemon=True).start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ================= HEADER =================
    def build_header(self):
        h = tk.Frame(self.root, bg=CARD, height=60)
        h.pack(fill=tk.X)

        self.title_lbl = tk.Label(
            h, 
            text="BTC / USDT",
            fg=TEXT, bg=CARD,
            font=("Segoe UI", 20, "bold")
        )
        self.title_lbl.pack(side=tk.LEFT, padx=14)

        self.price_lbl = tk.Label(
            h, fg=GREEN, bg=CARD,
            font=("Segoe UI", 20, "bold")
        )
        self.price_lbl.pack(side=tk.LEFT, padx=10)

        # ---- Panel toggles ----
        tk.Checkbutton(
            h, text="Volume",
            variable=self.show_volume,
            command=self.toggle_volume,
            bg=CARD, fg=TEXT, selectcolor=CARD,
            font=("Segoe UI", 12)
        ).pack(side=tk.RIGHT, padx=6)

        tk.Checkbutton(
            h, text="Order Book",
            variable=self.show_orderbook,
            command=self.toggle_orderbook,
            bg=CARD, fg=TEXT, selectcolor=CARD,
            font=("Segoe UI", 12)
        ).pack(side=tk.RIGHT, padx=6)

        tk.Checkbutton(
            h, text="Trades",
            variable=self.show_trades,
            command=self.toggle_trades,
            bg=CARD, fg=TEXT, selectcolor=CARD,
            font=("Segoe UI", 12)
        ).pack(side=tk.RIGHT, padx=6)

        for s in ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "ADAUSDT"):
            tk.Button(
                h, 
                text=s[:-4],
                font=("Segoe UI", 16),
                bg=CARD2, 
                fg=TEXT, bd=0,
                command=lambda x=s: self.select_symbol(x)
            ).pack(side=tk.RIGHT, padx=10)

    def toggle_volume(self):
        if self.show_volume.get():
            self.vol_5m.frame.grid()
            self.vol_1h.frame.grid()
        else:
            self.vol_5m.frame.grid_remove()
            self.vol_1h.frame.grid_remove()
        self.save_preferences()


    def toggle_orderbook(self):
        if self.show_orderbook.get():
            self.orderbook.frame.grid()
        else:
            self.orderbook.frame.grid_remove()
        self.save_preferences()



    def toggle_trades(self):
        if self.show_trades.get():
            self.trades_panel.frame.grid()
        else:
            self.trades_panel.frame.grid_remove()
        self.save_preferences()


    # ================= MAIN =================
    def build_main(self):
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill=tk.BOTH, expand=True)

        # ----- GRID STRUCTURE -----
        main.grid_columnconfigure(0, weight=1, uniform="main")
        main.grid_columnconfigure(1, weight=1, uniform="main")

        main.grid_rowconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=0)

        # ================= LEFT COLUMN =================
        left = tk.Frame(main, bg=BG)

        left.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        left.grid_columnconfigure(0, weight=1)

        # Control vertical space
        left.grid_rowconfigure(0, weight=2)  # 5 min
        left.grid_rowconfigure(1, weight=2)  # 1 hour
        left.grid_rowconfigure(2, weight=2)  # best bid/ask
        left.grid_rowconfigure(3, weight=5)  # order book (smaller than before)

        # Volume panels
        self.vol_5m = VolumeRatioPanel(left, "5 Minutes Volume & Ratio")
        self.vol_5m.frame.grid(row=0, column=0, sticky="nsew", pady=4)

        self.vol_1h = VolumeRatioPanel(left, "1 Hour Volume & Ratio")
        self.vol_1h.frame.grid(row=1, column=0, sticky="nsew", pady=4)

        # Best bid / ask
        self.best_price = BestPricePanel(left)
        self.best_price.frame.grid(row=2, column=0, sticky="nsew", pady=4)

        # Order book
        self.orderbook = OrderBookPanel(left, self.root)
        self.orderbook.frame.grid(row=3, column=0, sticky="nsew", pady=(6, 0))
        self.orderbook.set_best_price_callback(self.best_price.update)

        # ================= RIGHT COLUMN =================
        right = tk.Frame(main, bg=BG)
        right.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=0)  # Big price
        right.grid_rowconfigure(1, weight=0)  # 24h volume
        right.grid_rowconfigure(2, weight=1)  # Chart (expands)


        # Big price panel
        self.big_price = BigPricePanel(right)
        self.big_price.frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        # Vol_24h
        self.vol_24h = Volume24hPanel(right)
        self.vol_24h.frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        # Chart
        self.chart = CandlestickChart(right)
        self.chart.frame.grid(row=2, column=0, sticky="nsew")

        # ================= BOTTOM BAR (FULL WIDTH) =================
        bottom = tk.Frame(main, bg=BG, height=220)
        bottom.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8))
        bottom.grid_propagate(False)

        bottom.grid_columnconfigure(0, weight=1)  # LEFT (Live Trades)
        bottom.grid_columnconfigure(1, weight=1)  # RIGHT (Action panel)
        bottom.grid_rowconfigure(0, weight=1)

        # Live trades (left)
        self.trades_panel = TradesPanel(bottom, self.root)
        self.trades_panel.frame.grid(
            row=0, column=0,
            sticky="nsew",
            padx=(0, 6)
        )

        # Action panel (right)
        action = tk.Frame(bottom, bg=CARD, padx=16, pady=16)
        action.grid(
            row=0, column=1,
            sticky="nsew",
            padx=(6, 0)
        )

        tk.Label(
            action, text="Last Traded Price",
            fg=TEXT, bg=CARD, font=("Segoe UI", 13)
        ).pack(anchor="w")

        self.last_price_lbl = tk.Label(
            action, text="--",
            fg=TEXT, 
            bg=CARD,
            font=("Segoe UI", 16, "bold")
        )
        self.last_price_lbl.pack(anchor="w", pady=(4, 8))

        self.delta_lbl = tk.Label(
            action, text="",
            bg=CARD, font=("Segoe UI", 13, "bold")
        )
        self.delta_lbl.pack(anchor="w", pady=(0, 10))

        tk.Button(
            action, text="Trade",
            bg=ORANGE, fg="#000",
            font=("Segoe UI", 15, "bold"),
            bd=0, pady=8,
            command=self.open_trade
        ).pack(fill=tk.X)

        # Apply saved visibility
        self.toggle_volume()
        self.toggle_orderbook()
        self.toggle_trades()

    # ================= PRICE STREAM =================
    def start_price_stream(self):
        if self.price_ws:
            self.price_ws.keep_running = False
            self.price_ws.close()

        self.price_ws = websocket.WebSocketApp(
            f"wss://stream.binance.com:9443/ws/{self.current_symbol.lower()}@ticker",
            on_message=self.on_price,
            on_error=lambda ws, e: None,
            on_close=lambda ws, *a: None
        )
        threading.Thread(target=self.price_ws.run_forever, daemon=True).start()

    def on_price(self, ws, msg):
        if self.is_closing:
            return

        data = json.loads(msg)

        price = float(data["c"])
        change_24h = float(data["p"])
        percent_24h = float(data["P"])
        volume_24h = float(data["v"])

        self.root.after(
            0,
            self._update_from_price_stream,
            price,
            change_24h,
            percent_24h,
            volume_24h
        )

    def _update_from_price_stream(self, price, change_24h, percent_24h, volume_24h):
        self.update_price_ui(price, change_24h, percent_24h)
        self.vol_24h.update(volume_24h)

    def update_price_ui(self, price, change_24h, percent_24h):
        self.big_price.update(price, change_24h, percent_24h)
        self.price_lbl.config(text=f"{price:,.2f}")
        self.last_price_lbl.config(text=f"{price:,.2f}")

        p5 = self.get_5m_change()
        if p5:
            d = price - p5
            pct = d / p5 * 100
            arrow = "▲" if d > 0 else "▼" if d < 0 else ""
            color = GREEN if d > 0 else RED if d < 0 else MUTED

            self.delta_lbl.config(
                text=f"{arrow} {d:+.2f} ({pct:+.2f}%) · 5m",
                fg=color
            )

    # ================= HELPERS =================
    def select_symbol(self, symbol):
        self.current_symbol = symbol
        self.update_header()
        self.start_price_stream()
        self.trades_panel.start(symbol)
        self.orderbook.load(symbol)
        self.chart.load(symbol)
        
        # Load volume ratios in background threads
        threading.Thread(target=self._load_volumes, daemon=True).start()

    def _load_volumes(self):
        buy, sell = get_volume_ratio(self.current_symbol, 5)
        self.root.after(0, self.vol_5m.update, buy, sell)

        buy, sell = get_volume_ratio(self.current_symbol, 60)
        self.root.after(0, self.vol_1h.update, buy, sell)

    def update_header(self):
        self.title_lbl.config(
            text=f"{self.current_symbol[:-4]} / {self.current_symbol[-4:]}"
        )

    def open_trade(self):
        b, q = self.current_symbol[:-4], self.current_symbol[-4:]
        webbrowser.open(f"https://www.binance.com/en/trade/{b}_{q}")

    # def load_volume_ratio(self, minutes):
    #     try:
    #         url = "https://api.binance.com/api/v3/trades"
    #         params = {"symbol": self.current_symbol, "limit": 1000}

    #         resp = requests.get(url, params=params, timeout=5)
    #         if resp.status_code != 200:
    #             return 0.0, 0.0

    #         trades = resp.json()
    #         if not isinstance(trades, list):
    #             return 0.0, 0.0

    #         now = time.time()
    #         buy = sell = 0.0

    #         for t in trades:
    #             trade_time = t.get("time", 0) / 1000
    #             if now - trade_time > minutes * 60:
    #                 continue

    #             qty = float(t.get("qty", 0))
    #             if t.get("isBuyerMaker", False):
    #                 sell += qty
    #             else:
    #                 buy += qty

    #         return buy, sell

    #     except Exception as e:
    #         print("Volume ratio error:", e)
    #         return 0.0, 0.0

    def get_5m_change(self):
        if time.time() - self.last_5m_fetch < 30 and self.last_5m_price:
            return self.last_5m_price

        try:
            resp = requests.get(
                "https://api.binance.com/api/v3/klines",
                params={
                    "symbol": self.current_symbol,
                    "interval": "1m",
                    "limit": 6
                },
                timeout=5
            )

            if resp.status_code != 200:
                return None

            klines = resp.json()
            if not klines or not isinstance(klines, list):
                return None

            self.last_5m_price = float(klines[0][4])
            self.last_5m_fetch = time.time()
            return self.last_5m_price

        except Exception:
            return None

    def load_preferences(self):
        if not os.path.exists(PREF_FILE):
            return

        try:
            with open(PREF_FILE, "r") as f:
                prefs = json.load(f)

            self.show_volume.set(prefs.get("show_volume", True))
            self.show_orderbook.set(prefs.get("show_orderbook", True))
            self.show_trades.set(prefs.get("show_trades", True))

        except Exception as e:
            print("Failed to load preferences:", e)

    def save_preferences(self):
        prefs = {
            "show_volume": self.show_volume.get(),
            "show_orderbook": self.show_orderbook.get(),
            "show_trades": self.show_trades.get(),
        }

        try:
            with open(PREF_FILE, "w") as f:
                json.dump(prefs, f)
        except Exception as e:
            print("Failed to save preferences:", e)

    def on_close(self):
        self.is_closing = True
        self.save_preferences()

        if self.price_ws:
            try:
                self.price_ws.keep_running = False
                self.price_ws.close()
            except:
                pass

        if hasattr(self, "orderbook"):
            self.orderbook.alive = False

        if hasattr(self, "trades_panel"):
            self.trades_panel.stop()

        self.root.destroy()

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    r = tk.Tk()
    app = CryptoDashboard(r)
    r.mainloop()