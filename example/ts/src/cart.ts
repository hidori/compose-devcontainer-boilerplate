import { Item } from "./item.js";

export class Cart {
  private readonly items: Item[] = [];

  add(item: Item): void {
    this.items.push(item);
  }

  total(): number {
    return this.items.reduce((sum, item) => sum + item.subtotal(), 0);
  }
}
