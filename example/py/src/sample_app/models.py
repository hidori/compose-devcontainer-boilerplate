from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    name: str
    price: int
    quantity: int = 1

    def subtotal(self) -> int:
        return self.price * self.quantity
