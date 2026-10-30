from sample_app.cart import Cart
from sample_app.models import Item


def main() -> None:
    cart = Cart()
    cart.add(Item("apple", 120, 3))
    cart.add(Item("banana", 80))
    print(cart.total())


if __name__ == "__main__":
    main()
