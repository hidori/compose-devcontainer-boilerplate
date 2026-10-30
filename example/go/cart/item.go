package cart

type Item struct {
	Name     string
	Price    int
	Quantity int
}

func NewItem(name string, price int, quantity int) Item {
	return Item{Name: name, Price: price, Quantity: quantity}
}

func (i Item) Subtotal() int {
	return i.Price * i.Quantity
}
