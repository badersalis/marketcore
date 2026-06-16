from shared.base_exception import DomainException, ApplicationException


class OrderNotFoundException(DomainException):
    def __init__(self, order_id: str):
        super().__init__(f"Order {order_id!r} not found", "ORDER_NOT_FOUND")


class CartNotFoundException(DomainException):
    def __init__(self, user_id: str):
        super().__init__(f"Cart for user {user_id!r} not found", "CART_NOT_FOUND")


class OrderAlreadyCancelledException(DomainException):
    def __init__(self, order_id: str):
        super().__init__(f"Order {order_id!r} cannot be cancelled in its current state", "ORDER_NOT_CANCELLABLE")


class InvalidOrderStatusTransitionException(DomainException):
    def __init__(self, current, target):
        super().__init__(
            f"Cannot transition order from {current.value!r} to {target.value!r}",
            "INVALID_ORDER_TRANSITION",
        )


class InsufficientStockException(ApplicationException):
    def __init__(self, product_id: str, requested: int, available: int):
        super().__init__(
            f"Insufficient stock for product {product_id!r}: requested {requested}, available {available}",
            status_code=409,
        )


class EmptyCartException(DomainException):
    def __init__(self):
        super().__init__("Cannot place order from an empty cart", "EMPTY_CART")


__all__ = [
    "OrderNotFoundException",
    "CartNotFoundException",
    "OrderAlreadyCancelledException",
    "InvalidOrderStatusTransitionException",
    "InsufficientStockException",
    "EmptyCartException",
]
