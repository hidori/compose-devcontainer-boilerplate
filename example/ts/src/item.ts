export class Item {
  constructor(
    readonly name: string,
    readonly price: number,
    readonly quantity: number = 1,
  ) {}

  subtotal(): number {
    return this.price * this.quantity;
  }
}
