from decimal import Decimal, InvalidOperation


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class ValidationError(Exception):
    pass


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol or not symbol.isalnum():
        raise ValidationError(f"Invalid symbol '{symbol}'. Must be alphanumeric (e.g. BTCUSDT).")
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity: str) -> Decimal:
    try:
        qty = Decimal(str(quantity))
        if qty <= 0:
            raise ValidationError("Quantity must be a positive number.")
        return qty
    except InvalidOperation:
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")


def validate_price(price: str) -> Decimal:
    try:
        p = Decimal(str(price))
        if p <= 0:
            raise ValidationError("Price must be a positive number.")
        return p
    except InvalidOperation:
        raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")


def validate_stop_price(stop_price: str) -> Decimal:
    return validate_price(stop_price)
