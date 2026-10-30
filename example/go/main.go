package main

import (
	"fmt"

	"example.com/sampleapp/cart"
)

func main() {
	var c cart.Cart
	c.Add(cart.NewItem("apple", 120, 3))
	c.Add(cart.NewItem("banana", 80, 1))
	fmt.Println(c.Total())
}
