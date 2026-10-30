using SampleApp;

var cart = new Cart();
cart.Add(new Item("apple", 120, 3));
cart.Add(new Item("banana", 80));
Console.WriteLine(cart.Total());
