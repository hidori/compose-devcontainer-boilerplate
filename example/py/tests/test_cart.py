from sample_app.cart import Cart
from sample_app.models import Item


def test_total() -> None:
    cart = Cart()
    cart.add(Item("apple", 120, 3))
    cart.add(Item("banana", 80))
    assert cart.total() == 440
