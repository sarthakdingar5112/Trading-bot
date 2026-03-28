#!/usr/bin/env python3
"""
Trading Bot CLI — Binance Futures Testnet
"""

import argparse
import os
import sys

from bot.client import BinanceFuturesClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.orders import (
    place_market_order,
    place_limit_order,
    place_stop_market_order,
    print_order_response,
)
from bot.validators import (
    ValidationError,
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
)

logger = setup_logger()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  Market BUY:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  Limit SELL:
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000

  Stop-Market BUY (bonus):
    python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 68000

API credentials can be set via --api-key / --api-secret flags
or environment variables BINANCE_API_KEY / BINANCE_API_SECRET.
        """,
    )

    parser.add_argument("--api-key",    type=str, default=None, help="Binance Testnet API key")
    parser.add_argument("--api-secret", type=str, default=None, help="Binance Testnet API secret")
    parser.add_argument("--symbol",     type=str, required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side",       type=str, required=True, help="BUY or SELL")
    parser.add_argument("--type",       type=str, required=True, dest="order_type",
                        help="MARKET | LIMIT | STOP_MARKET")
    parser.add_argument("--quantity",   type=str, required=True, help="Order quantity")
    parser.add_argument("--price",      type=str, default=None,
                        help="Limit price (required for LIMIT orders)")
    parser.add_argument("--stop-price", type=str, default=None, dest="stop_price",
                        help="Stop price (required for STOP_MARKET orders)")

    return parser


def resolve_credentials(args: argparse.Namespace):
    api_key    = args.api_key    or os.environ.get("BINANCE_API_KEY")
    api_secret = args.api_secret or os.environ.get("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        print(
            "\nERROR: API credentials not found.\n"
            "Provide them via --api-key / --api-secret flags or set the\n"
            "BINANCE_API_KEY and BINANCE_API_SECRET environment variables.\n"
        )
        sys.exit(1)

    return api_key, api_secret


def main():
    parser = build_parser()
    args   = parser.parse_args()

    # ── Validate inputs ──────────────────────────────────────────────── #
    try:
        symbol     = validate_symbol(args.symbol)
        side       = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity   = validate_quantity(args.quantity)

        price      = validate_price(args.price)      if args.price      else None
        stop_price = validate_stop_price(args.stop_price) if args.stop_price else None

        if order_type == "LIMIT" and price is None:
            raise ValidationError("--price is required for LIMIT orders.")

        if order_type == "STOP_MARKET" and stop_price is None:
            raise ValidationError("--stop-price is required for STOP_MARKET orders.")

    except ValidationError as exc:
        logger.error("Validation error: %s", exc)
        print(f"\nValidation Error: {exc}\n")
        sys.exit(1)

    # ── Credentials ──────────────────────────────────────────────────── #
    api_key, api_secret = resolve_credentials(args)

    # ── Place order ──────────────────────────────────────────────────── #
    client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)

    try:
        if order_type == "MARKET":
            response = place_market_order(client, symbol, side, quantity)
        elif order_type == "LIMIT":
            response = place_limit_order(client, symbol, side, quantity, price)
        elif order_type == "STOP_MARKET":
            response = place_stop_market_order(client, symbol, side, quantity, stop_price)
        else:
            raise ValidationError(f"Unhandled order type: {order_type}")

        print_order_response(response)
        logger.info("Order placed successfully. Order ID: %s | Status: %s",
                    response.get("orderId"), response.get("status"))
        print("\n  ✓ Order placed successfully!\n")

    except BinanceClientError as exc:
        logger.error("Order failed: %s", exc)
        print(f"\n  ✗ Order failed: {exc}\n")
        sys.exit(1)

    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        print(f"\n  ✗ Unexpected error: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
