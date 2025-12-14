import tkinter as tk
import threading
from utils.binance_api import get_orderbook
from config import *

class OrderBookPanel:
    def __init__(self, parent, root):
        self.root = root
        self.frame = tk.Frame(parent, bg=CARD)
        self.alive = True
        self.on_best_price = None

        tk.Label(
            self.frame, text="Order Book",
            fg=TEXT, bg=CARD,
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", padx=12, pady=(10, 6))

        container = tk.Frame(self.frame, bg=CARD)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.bids = tk.Text(container, bg=BG, fg=GREEN, relief="flat")
        self.asks = tk.Text(container, bg=BG, fg=RED, relief="flat")
        self.bids.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.asks.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

    def load(self, symbol):
        threading.Thread(
            target=self._worker,
            args=(symbol,),
            daemon=True
        ).start()

    def _worker(self, symbol):
        if not self.alive:
            return

        data = get_orderbook(symbol)
        bids = data.get("bids", [])
        asks = data.get("asks", [])

        if bids and asks and self.on_best_price:
            best_bid = float(bids[0][0])
            best_ask = float(asks[0][0])

            self.root.after(
                0,
                self.on_best_price,
                best_bid,
                best_ask
            )

        self.root.after(0, self.update, bids, asks)


    def update(self, bids, asks):
        self.bids.delete("1.0", tk.END)
        self.asks.delete("1.0", tk.END)
        for p, _ in bids:
            self.bids.insert(tk.END, f"{float(p):,.2f}\n")
        for p, _ in asks:
            self.asks.insert(tk.END, f"{float(p):,.2f}\n")

    def set_best_price_callback(self, callback):
        self.on_best_price = callback