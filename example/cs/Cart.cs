namespace SampleApp;

public sealed class Cart
{
    private readonly List<Item> _items = [];

    public void Add(Item item) => _items.Add(item);

    public int Total() => _items.Sum(item => item.Subtotal());
}
