from tdd_shopping_cart import Product, ShoppingCart


def build_books_cart(quantity: int = 3) -> ShoppingCart:
    cart = ShoppingCart()
    cart.add(Product("book", "ksiazka", "books", 5000), quantity)
    return cart


def total_with_three_for_two(quantity: int = 3) -> int:
    cart = build_books_cart(quantity)
    cart.enable_three_for_two("books")
    return cart.total_cents()
