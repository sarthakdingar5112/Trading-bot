# Trading Bot — Binance Futures Testnet (USDT-M)

A lightweight Python CLI application to place MARKET, LIMIT, and STOP_MARKET orders on the Binance Futures Testnet.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper
│   ├── orders.py          # Order placement logic & response printing
│   ├── validators.py      # Input validation
│   └── logging_config.py  # Structured file + console logging
├── cli.py                 # CLI entry point (argparse)
├── logs/                  # Auto-created; one log file per day
├── README.md
└── requirements.txt
```

---

## Setup

### 1. Get Testnet Credentials

1. Visit [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Sign in with GitHub
3. Go to **API Key** section and generate a key pair

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Credentials

**Option A — Environment variables (recommended):**
```bash
export BINANCE_API_KEY="your_api_key_here"
export BINANCE_API_SECRET="your_api_secret_here"
```

**Option B — CLI flags:**
```bash
python cli.py --api-key YOUR_KEY --api-secret YOUR_SECRET ...
```

---

## Usage

```
python cli.py --symbol SYMBOL --side SIDE --type TYPE --quantity QTY [options]
```

| Flag           | Required | Description                          |
|----------------|----------|--------------------------------------|
| `--symbol`     | Yes      | Trading pair (e.g. `BTCUSDT`)        |
| `--side`       | Yes      | `BUY` or `SELL`                      |
| `--type`       | Yes      | `MARKET`, `LIMIT`, or `STOP_MARKET`  |
| `--quantity`   | Yes      | Order quantity                       |
| `--price`      | LIMIT    | Limit price (required for LIMIT)     |
| `--stop-price` | STOP     | Trigger price (required for STOP_MARKET) |
| `--api-key`    | No*      | Override env var                     |
| `--api-secret` | No*      | Override env var                     |

---

## Examples

**Market BUY:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Limit SELL:**
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 85000
```

**Stop-Market BUY (bonus order type):**
```bash
python cli.py --symbol ETHUSDT --side BUY --type STOP_MARKET --quantity 0.01 --stop-price 3100
```

---

## Sample Output

```
=============================================
  ORDER REQUEST SUMMARY
=============================================
Symbol   : BTCUSDT
Side     : BUY
Type     : MARKET
Quantity : 0.001
=============================================

=============================================
  ORDER RESPONSE
=============================================
  Order ID       : 4751382910
  Symbol         : BTCUSDT
  Status         : FILLED
  Type           : MARKET
  Side           : BUY
  Orig. Qty      : 0.001
  Executed Qty   : 0.001
  Avg. Price     : 83412.50000
=============================================

  ✓ Order placed successfully!
```

---

## Logging

Logs are written to `logs/trading_bot_YYYYMMDD.log`.  
Each log entry includes a timestamp, log level, module name, and message.  
The console shows INFO-level and above; the file captures DEBUG-level (full request/response bodies).

---

## Assumptions

- All orders target the USDT-M perpetual futures market on the Binance Testnet.
- LIMIT orders use `timeInForce=GTC` (Good Till Cancelled) by default.
- Quantity precision should conform to the symbol's lot size filter. If the API rejects an order due to precision, adjust your quantity accordingly.
- No position management, leverage setting, or account balance check is performed — this is a focused order-placement tool.

---

## Dependencies

- `requests` — HTTP client for REST API calls  
- Python standard library only (no third-party Binance SDK required)
