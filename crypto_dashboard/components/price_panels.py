import tkinter as tk
import websocket
import json
import threading
from config import *

class BigPricePanel:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=CARD, padx=16, pady=8)

        self.arrow_lbl = tk.Label(
            self.frame,
            text="",
            font=("Segoe UI", 20, "bold"),
            bg=CARD
        )
        self.arrow_lbl.pack(side=tk.LEFT, padx=(0, 8))

        self.price_lbl = tk.Label(
            self.frame,
            text="--",
            font=("Segoe UI", 35, "bold"),
            bg=CARD
        )
        self.price_lbl.pack(side=tk.LEFT)

        self.prev_price = None

        self.change_lbl = tk.Label(
            self.frame,
            text="",
            bg=CARD,
            font=("Segoe UI", 13, "bold")
        )
        self.change_lbl.pack(anchor="w", padx=(36, 0))

    def update(self, price, change=None, percent=None):
        if self.prev_price is None:
            self.prev_price = price

        if price > self.prev_price:
            color = GREEN
            arrow = "▲"
        elif price < self.prev_price:
            color = RED
            arrow = "▼"
        else:
            color = MUTED
            arrow = ""

        self.arrow_lbl.config(text=arrow, fg=color)
        self.price_lbl.config(text=f"{price:,.2f}", fg=color)

        if change is not None and percent is not None:
            self.change_lbl.config(
                text=f"{arrow} {change:+.2f} ({percent:+.2f}%) · 24h",
                fg=color
            )

        self.prev_price = price

class TradesPanel:
    def __init__(self, parent, root):
        self.root = root
        self.frame = tk.Frame(parent, bg=CARD)

        title = tk.Label(self.frame, text="Live Trades", fg=TEXT, bg=CARD,
                         font=("Segoe UI", 15, "bold"))
        title.pack(anchor="w", padx=12, pady=(10, 6))

        self.text = tk.Text(self.frame, height=8, bg=BG, fg=TEXT,
                            insertbackground=TEXT, relief="flat")
        self.text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.text.config(state=tk.DISABLED)

        self.ws = None
        self.active = False

    def start(self, symbol):
        self.stop()
        self.active = True
        url = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@trade"
        self.ws = websocket.WebSocketApp(url, on_message=self.on_message)
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def stop(self):
        self.active = False
        if self.ws:
            try:
                self.ws.keep_running = False
                self.ws.close()
            except:
                pass
            self.ws = None

    def on_message(self, ws, message):
        if not self.active:
            return
        data = json.loads(message)
        price = float(data["p"])
        qty = float(data["q"])
        side = "SELL" if data["m"] else "BUY"
        try:
            self.root.after(0, self.add_trade, price, qty, side)
        except tk.TclError:
            pass

    def add_trade(self, price, qty, side):
        color = RED if side == "SELL" else GREEN
        self.text.config(state=tk.NORMAL)
        if int(self.text.index("end-1c").split(".")[0]) > 200:
            self.text.delete("1.0", "20.0")
        self.text.insert(tk.END, f"{side:<4}  {price:,.2f}  ({qty:.4f})\n")
        self.text.tag_add(side, "end-2l", "end-1l")
        self.text.tag_config(side, foreground=color)
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

class BestPricePanel:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=CARD, padx=12, pady=4)

        tk.Label(
            self.frame,
            text="Best Bid / Ask",
            fg=TEXT,
            bg=CARD,
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w")


        self.bid_var = tk.StringVar(value="-")
        self.ask_var = tk.StringVar(value="-")
        self.spread_var = tk.StringVar(value="-")

        grid = tk.Frame(self.frame, bg=CARD)
        grid.pack(fill=tk.X, pady=2)

        grid.grid_rowconfigure(3, minsize=0)

        tk.Label(grid, text="Best Bid", fg=GREEN, bg=CARD, font=("Segoe UI", 13)).grid(row=0, column=0, sticky="w")
        tk.Label(
            grid,
            textvariable=self.bid_var,
            fg=GREEN,
            bg=CARD,
            font=("Segoe UI", 13, "bold")
        ).grid(row=0, column=1, sticky="e")

        tk.Label(grid, text="Best Ask", fg=RED, bg=CARD, font=("Segoe UI", 13)).grid(row=1, column=0, sticky="w")
        tk.Label(
            grid,
            textvariable=self.ask_var,
            fg=RED,
            bg=CARD,
            font=("Segoe UI", 13, "bold")
        ).grid(row=1, column=1, sticky="e")

        tk.Label(grid, text="Spread", fg=ORANGE, bg=CARD, font=("Segoe UI", 13)).grid(row=2, column=0, sticky="w")
        tk.Label(
            grid,
            textvariable=self.spread_var,
            fg=ORANGE,
            bg=CARD,
            font=("Segoe UI", 13 ,"bold")
        ).grid(row=2, column=1, sticky="e")
        
        grid.columnconfigure(1, weight=1)

    def update(self, best_bid, best_ask):
        spread = best_ask - best_bid
        self.bid_var.set(f"{best_bid:,.2f}")
        self.ask_var.set(f"{best_ask:,.2f}")
        self.spread_var.set(f"{spread:.2f}")
