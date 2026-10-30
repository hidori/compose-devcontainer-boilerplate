from sample_app.models import Item


class Cart:
    def __init__(self) -> None:
        self._items: list[Item] = []

    def add(self, item: Item) -> None:
        self._items.append(item)

    def total(self) -> int:
        return sum(item.subtotal() for item in self._items)
