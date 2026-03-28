from decimal import Decimal
from typing import Any, Dict, Optional

from bot.client import BinanceFuturesClient
from bot.logging_config import setup_logger

logger = setup_logger()


def _build_order_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: Decimal,
    price: Optional[Decimal] = None,
    stop_price: Optional[Decimal] = None,
) -> str:
    parts = [
        f"Symbol   : {symbol}",
        f"Side     : {side}",
        f"Type     : {order_type}",
        f"Quantity : {quantity}",
    ]
    if price is not None:
        parts.append(f"Price    : {price}")
    if stop_price is not None:
        parts.append(f"Stop     : {stop_price}")
    return "\n".join(parts)


def place_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: Decimal,
) -> Dict[str, Any]:
    summary = _build_order_summary(symbol, side, "MARKET", quantity)
    logger.info("Placing MARKET order:\n%s", summary)
    print(f"\n{'='*45}")
    print("  ORDER REQUEST SUMMARY")
    print(f"{'='*45}")
    print(summary)
    print(f"{'='*45}")

    response = client.new_order(
        symbol=symbol,
        side=side,
        type="MARKET",
        quantity=str(quantity),
    )
    return response


def place_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: Decimal,
    price: Decimal,
) -> Dict[str, Any]:
    summary = _build_order_summary(symbol, side, "LIMIT", quantity, price=price)
    logger.info("Placing LIMIT order:\n%s", summary)
    print(f"\n{'='*45}")
    print("  ORDER REQUEST SUMMARY")
    print(f"{'='*45}")
    print(summary)
    print(f"{'='*45}")

    response = client.new_order(
        symbol=symbol,
        side=side,
        type="LIMIT",
        quantity=str(quantity),
        price=str(price),
        timeInForce="GTC",
    )
    return response


def place_stop_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: Decimal,
    stop_price: Decimal,
) -> Dict[str, Any]:
    """Bonus: Stop-Market order type."""
    summary = _build_order_summary(symbol, side, "STOP_MARKET", quantity, stop_price=stop_price)
    logger.info("Placing STOP_MARKET order:\n%s", summary)
    print(f"\n{'='*45}")
    print("  ORDER REQUEST SUMMARY")
    print(f"{'='*45}")
    print(summary)
    print(f"{'='*45}")

    response = client.new_order(
        symbol=symbol,
        side=side,
        type="STOP_MARKET",
        quantity=str(quantity),
        stopPrice=str(stop_price),
    )
    return response


def print_order_response(response: Dict[str, Any]) -> None:
    """Pretty-print the order response fields."""
    print(f"\n{'='*45}")
    print("  ORDER RESPONSE")
    print(f"{'='*45}")
    fields = [
        ("Order ID",       response.get("orderId", "N/A")),
        ("Symbol",         response.get("symbol", "N/A")),
        ("Status",         response.get("status", "N/A")),
        ("Type",           response.get("type", "N/A")),
        ("Side",           response.get("side", "N/A")),
        ("Orig. Qty",      response.get("origQty", "N/A")),
        ("Executed Qty",   response.get("executedQty", "N/A")),
        ("Avg. Price",     response.get("avgPrice", "N/A")),
        ("Price",          response.get("price", "N/A")),
        ("Time in Force",  response.get("timeInForce", "N/A")),
        ("Update Time",    response.get("updateTime", "N/A")),
    ]
    for label, value in fields:
        if value not in ("N/A", "", None, "0", "0.00000"):
            print(f"  {label:<15}: {value}")
    print(f"{'='*45}")
