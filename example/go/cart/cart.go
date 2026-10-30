package cart

type Cart struct {
	items []Item
}

func (c *Cart) Add(item Item) {
	c.items = append(c.items, item)
}

func (c *Cart) Total() int {
	total := 0
	for _, item := range c.items {
		total += item.Subtotal()
	}
	return total
}
