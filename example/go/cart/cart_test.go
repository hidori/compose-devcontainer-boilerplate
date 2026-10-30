package cart

import "testing"

func TestTotal(t *testing.T) {
	var c Cart
	c.Add(NewItem("apple", 120, 3))
	c.Add(NewItem("banana", 80, 1))
	if got := c.Total(); got != 440 {
		t.Errorf("Total() = %d, want 440", got)
	}
}
