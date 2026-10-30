import { Cart } from "./cart.js";
import { Item } from "./item.js";

const cart = new Cart();
cart.add(new Item("apple", 120, 3));
cart.add(new Item("banana", 80));
console.log(cart.total());
