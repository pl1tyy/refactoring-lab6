# Константы
TAX_RATE = 0.21
DEFAULT_CURRENCY = "USD"
MIN_SUBTOTAL_FOR_SAVE20 = 200
VIP_DISCOUNT_HIGH = 50
VIP_DISCOUNT_LOW = 10


def _validate_request(request: dict):
    """Проверяет обязательные поля запроса."""
    if request.get("user_id") is None:
        raise ValueError("user_id is required")
    if request.get("items") is None:
        raise ValueError("items is required")


def _validate_items(items):
    """Проверяет корректность списка товаров."""
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")
    
    for item in items:
        if "price" not in item or "qty" not in item:
            raise ValueError("item must have price and qty")
        if item["price"] <= 0:
            raise ValueError("price must be positive")
        if item["qty"] <= 0:
            raise ValueError("qty must be positive")


def _calculate_subtotal(items):
    """Считает промежуточную сумму."""
    return sum(item["price"] * item["qty"] for item in items)


def _calculate_discount(coupon: str, subtotal: int) -> int:
    """Рассчитывает скидку по купону."""
    if not coupon:  # Обрабатывает None и пустую строку
        return 0
    
    if coupon == "SAVE10":
        return int(subtotal * 0.10)
    
    if coupon == "SAVE20":
        if subtotal >= MIN_SUBTOTAL_FOR_SAVE20:
            return int(subtotal * 0.20)
        else:
            return int(subtotal * 0.05)
    
    if coupon == "VIP":
        return VIP_DISCOUNT_HIGH if subtotal >= 100 else VIP_DISCOUNT_LOW
    
    raise ValueError("unknown coupon")


def _generate_order_id(user_id, items_count):
    """Генерирует ID заказа."""
    return f"{user_id}-{items_count}-X"


def process_checkout(request: dict) -> dict:
    """Обрабатывает оформление заказа."""
    _validate_request(request)
    
    user_id = request["user_id"]
    items = request["items"]
    coupon = request.get("coupon")
    currency = request.get("currency", DEFAULT_CURRENCY)
    
    _validate_items(items)
    
    subtotal = _calculate_subtotal(items)
    discount = _calculate_discount(coupon, subtotal)
    
    total_after_discount = max(0, subtotal - discount)
    tax = int(total_after_discount * TAX_RATE)
    total = total_after_discount + tax
    
    order_id = _generate_order_id(user_id, len(items))
    
    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }