Crypto Dashboard Project (Tkinter + APIs + OOP)
===================================================
This project is built to practice Python object-oriented programming, GUI development with Tkinter, and real-time data handling using the Binance REST and WebSocket APIs.
The dashboard displays live cryptocurrency market data such as prices, volumes, order books, and charts, organized into reusable UI components across multiple files.

-----------------------------------------------------
Features
-----------------------------------------------------
1. CORE REQUIREMENTS (MET)
✓ Application launches without errors
✓ Clean Object-Oriented Programming (OOP) design
✓ Modular file structure (components, utils, config)
✓ Proper event handling (buttons, toggles, window events)
✓ Graceful shutdown
  - WebSocket connections are closed safely
  - Background threads do not crash the UI
  - User preferences are saved on exit

2. PRICE TICKERS (MET)
✓ Supports multiple cryptocurrencies:
  - BTC / USDT
  - ETH / USDT
  - SOL / USDT
  - BNB / USDT
  - ADA / USDT
✓ Real-time price updates using Binance WebSocket API
✓ Color-coded price movement (green/red)
✓ 24-hour price change and percentage display
✓ Large price display panel for readability

3. USER INTERFACE (MET)
✓ Professional, organized dashboard layout
✓ Responsive layout using grid and weight configuration
✓ Clear labels and consistent color theme
✓ Toggle buttons to show/hide panels:
  - Volume panels
  - Order Book
  - Trades panel

4. ADDITIONAL DATA STREAMS (MET)
✓ 24-hour trading volume display
✓ Order Book panel (top bids and asks)
✓ Live Trades feed (real-time updates)
✓ Candlestick chart with volume (matplotlib)

5. MULTIPLE ASSETS & TOGGLES (MET)
✓ Supports more than 5 cryptocurrencies
✓ Individual buttons to switch assets
✓ Saved user preferences:
  - Panel visibility is remembered between runs
  - Preferences stored in a local JSON file

6. INFORMATION DENSITY (MET)
✓ Displays comprehensive market information at once
✓ Multiple panels showing different data types
✓ Efficient use of screen space without clutter

EXTRA FEATURES

The following features go BEYOND the assignment’s core requirements:

✓ Modular architecture:
  - Refactored from a single file into multiple modules
  - Clear separation between UI, API logic, and configuration

✓ Centralized API utilities:
  - Binance REST API logic isolated in utils/binance_api.py
  - Improves maintainability and readability

✓ Thread-safe UI updates:
  - All background data updates use root.after()
  - Prevents Tkinter threading errors

✓ Preference persistence:
  - User UI choices are saved automatically
  - Application restores state on next launch

✓ Clean shutdown handling:
  - WebSocket streams are explicitly stopped
  - Prevents orphan threads and runtime errors

✓ Scalable design:
  - New panels or indicators can be added easily
  - New symbols can be added by updating config.py

-----------------------------------------------------
Project Structure
-----------------------------------------------------
crypto_dashboard/
│
├── main.py                  # Application entry point
├── config.py                # Colors, symbols, preferences file
├── requirements.txt         # Python dependencies
│
├── components/
│   ├── __init__.py
│   ├── orderbook.py         # OrderBookPanel
│   ├── price_panels.py      # BigPricePanel, TradesPanel, BestPricePanel
│   └── technical.py         # Charts and volume-related panels
│
├── utils/
│   ├── __init__.py
│   └── binance_api.py       # Binance REST API helper functions
│
└── README.md

-------------------------------------------------------
How to Run the Project
-------------------------------------------------------
1. Create and activate a virtual environment (recommended)
Install dependencies:
pip install -r requirements.txt
2. Run the application:
python main.py
3.The dashboard window should open and start streaming live data.

--------------------------------------------------------
How to use the dashboard
--------------------------------------------------------
-Select a cryptocurrency
Click on the buttons at the top (BTC, ETH, SOL, BNB, ADA) to switch assets.
Live price updates
Prices update in real time using Binance WebSocket streams.
-Panel toggles
Use the checkboxes at the top to show or hide:
   Volume panels
   Order Book
   Trades panel
-Market data displayed
   Current price and 24h change
   24-hour trading volume
   Best bid / ask and spread
   Order book (top bids and asks)
   Recent trades
   Candlestick chart with volume
-Preferences
Panel visibility is saved automatically.
When you reopen the app, your previous layout is restored.
-Trade button
Opens the Binance trading page for the selected pair in your browser.

------------------------------------------------------
Report
------------------------------------------------------
I have correctly implemented all the code
The application runs without errors.
The project uses clean object-oriented design with separate components.
Live data is retrieved using Binance REST and WebSocket APIs.
The user interface is responsive and organized.
All required features from the assignment specification are implemented.
Preferences are saved and restored correctly.
