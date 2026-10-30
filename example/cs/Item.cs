namespace SampleApp;

public sealed record Item(string Name, int Price, int Quantity = 1)
{
    public int Subtotal() => Price * Quantity;
}
