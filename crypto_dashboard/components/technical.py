import tkinter as tk
import threading
from config import *
from utils.binance_api import get_klines
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CandlestickChart:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=BG)
        self.frame.grid_propagate(True)
        self.figure, (self.ax, self.vax) = plt.subplots(
            2, 1,
            sharex=True,
            gridspec_kw={"height_ratios": [3, 1]}
        )

        self.figure.patch.set_facecolor(BG)
        for a in (self.ax, self.vax):
            a.set_facecolor(BG)
            a.tick_params(colors=MUTED)
            for s in a.spines.values():
                s.set_visible(False)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load(self, symbol):
        klines = get_klines(symbol, interval="1m", limit=60)
        self.symbol = symbol
        self.draw(klines)


    def draw(self, klines):
        self.ax.clear(); self.vax.clear()
        prices = []
        for i, k in enumerate(klines):
            o, h, l, c, v = map(float, (k[1], k[2], k[3], k[4], k[5]))
            prices += [o, h, l, c]
            col = GREEN if c >= o else RED
            self.ax.plot([i, i], [l, h], color=col, lw=1)
            self.ax.bar(i, abs(c - o), bottom=min(o, c), width=0.6, color=col)
            self.vax.bar(i, v, width=0.6, color=col, alpha=0.4)
        self.ax.set_ylim(min(prices) * 0.999, max(prices) * 1.001)
        base = self.symbol[:-4]
        quote = self.symbol[-4:]
        self.ax.set_title(f"{base} / {quote}", color=TEXT, loc="left")
        self.canvas.draw_idle()

class VolumeRatioPanel:
    def __init__(self, parent, title):
        self.frame = tk.Frame(parent, bg=CARD, padx=12, pady=2)

        tk.Label(
            self.frame,
            text=title,
            font=("Segoe UI", 15, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(anchor="w")


        self.buy_var = tk.StringVar(value="0.00")
        self.sell_var = tk.StringVar(value="0.00")
        self.ratio_var = tk.StringVar(value="0.000")

        grid = tk.Frame(self.frame, bg=CARD)
        grid.pack(fill=tk.X, pady=0)

        tk.Label(grid, text="Buy", fg=GREEN, bg=CARD, font=("Segoe UI", 13)).grid(row=0, column=0, sticky="w")
        tk.Label(grid, textvariable=self.buy_var, fg=TEXT, bg=CARD, font=("Segoe UI", 13)).grid(row=0, column=1, sticky="e")

        tk.Label(grid, text="Sell", fg=RED, bg=CARD, font=("Segoe UI", 13)).grid(row=1, column=0, sticky="w")
        tk.Label(grid, textvariable=self.sell_var, fg=TEXT, bg=CARD, font=("Segoe UI", 13)).grid(row=1, column=1, sticky="e")

        tk.Label(grid, text="Ratio", fg=ORANGE, bg=CARD, font=("Segoe UI", 13)).grid(row=2, column=0, sticky="w")
        tk.Label(grid, textvariable=self.ratio_var, fg=TEXT, bg=CARD, font=("Segoe UI", 13)).grid(row=2, column=1, sticky="e")

        grid.columnconfigure(1, weight=1)

    def update(self, buy, sell):
        total = buy + sell
        ratio = buy / total if total > 0 else 0

        self.buy_var.set(f"{buy:.2f}")
        self.sell_var.set(f"{sell:.2f}")
        self.ratio_var.set(f"{ratio:.3f}")

class Volume24hPanel:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=CARD, padx=12, pady=6)

        tk.Label(
            self.frame,
            text="24H VOLUME",
            fg=MUTED,
            bg=CARD,
            font=("Segoe UI", 12)
        ).pack(anchor="w")

        self.value_lbl = tk.Label(
            self.frame,
            text="--",
            fg=TEXT,
            bg=CARD,
            font=("Segoe UI", 16, "bold")
        )
        self.value_lbl.pack(anchor="w")

    def update(self, volume):
        self.value_lbl.config(text=f"{volume:,.2f}")

