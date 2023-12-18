"""Цей модуль містить початковий код для тестування класу Customer.
"""
from store import Customer
from store import Item


def test_customer_init() -> None:
    """Перевіряє ініціалізатор класу клієнтів."""
    i1 = Item('mango', 1)
    i2 = Item('mango', 1)
    c = Customer('Valeriy', [i1, i2])
    assert c.name == 'Valeriy'
    assert c.arrival_time == -1
    assert c._items[0] == i1
    assert c._items[1] == i2

def test_customer_num_items() -> None:
    """Перевіряє num_items класу клієнтів."""
    c1 = Customer('Valeriy', [Item('bananas', 7), Item('mango', 1)])
    c2 = Customer('Anton', [])
    assert c1.num_items() == 2
    assert c2.num_items() == 0

def test_customer_get_item_time() -> None:
    """Перевіряє get_item_time класу клієнта."""
    c1 = Customer('Valeriy', [Item('bananas', 7), Item('mango', 1)])
    c2 = Customer('Anton', [])
    assert c1.get_item_time() == 8
    assert c2.get_item_time() == 0

if __name__ == '__main__':
    import pytest
    pytest.main(['test_customer.py'])
