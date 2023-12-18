"""
Цей модуль містить усі класи, необхідні для моделювання об’єктів у продуктовому магазині.
"""
from __future__ import annotations
from typing import List, Optional, TextIO
import json

EXPRESS_LIMIT = 7


class GroceryStore:
    """Продуктовий магазин.

     Приватні атрибути
     _regular_count: кількість регулярних касових ліній
     _express_count: кількість ліній швидкої каси
     _self_serve_count: кількість черг каси самообслуговування
     _line_capacity: максимальна місткість усіх ліній
     _checkout_lines: список кас у цьому продуктовому магазині
    """
    _regular_count: int
    _express_count: int
    _self_serve_count: int
    _line_capacity: int
    _checkout_lines: List[CheckoutLine]

    def __init__(self, config_file: TextIO) -> None:
        """Ініціалізуйте GroceryStore із файлу конфігурації <config_file>.
        """
        j = json.load(config_file)
        self._regular_count = j['regular_count']
        self._express_count = j['express_count']
        self._self_serve_count = j['self_serve_count']
        self._line_capacity = j['line_capacity']
        self._checkout_lines = []

        for _ in range(self._regular_count):
            self._checkout_lines.append(RegularLine(self._line_capacity))
        for _ in range(self._express_count):
            self._checkout_lines.append(ExpressLine(self._line_capacity))
        for _ in range(self._self_serve_count):
            self._checkout_lines.append(SelfServeLine(self._line_capacity))

    def enter_line(self, customer: Customer) -> int:
        """Вибирає новий рядок, щоб <клієнт> приєднався.

         Повертає індекс рядка, до якого приєднався клієнт.
         Необхідно скористатися алгоритмом із роздаткового матеріалу.

         Повертає -1, якщо немає лінії, до якої клієнт може приєднатися.
        """
        smallest = self._line_capacity + 1
        enter = 0
        for line in self._checkout_lines:
            size = len(line)
            if size < smallest and line.can_accept(customer):
                smallest = size
                enter = line
        if enter == 0:
            return -1
        else:
            enter.accept(customer)
            return self._checkout_lines.index(enter)

    def line_is_ready(self, line_number: int) -> bool:
        """Таким чином, line_is_ready має повертати True тоді і тільки тоді, коли в черзі точно один клієнт.
        """
        if len(self._checkout_lines[line_number]) == 1:
            return True
        else:
            return False

    def start_checkout(self, line_number: int) -> int:
        """Повертає час, який знадобиться для перевірки наступного клієнта в рядку <line_number> Попередня умова: у вказаному рядку є клієнт.
        """
        return self._checkout_lines[line_number].start_checkout()

    def complete_checkout(self, line_number: int) -> bool:
        """ Повертає True, якщо в рядку <line_number> залишилися клієнти, яких потрібно розрахувати
        """
        return self._checkout_lines[line_number].complete_checkout()

    def close_line(self, line_number: int) -> List[Customer]:
        """Закриває рядок <line_number> і поверніть клієнтів із тієї черги, які все ще чекають на розрахунок.
        """
        return self._checkout_lines[line_number].close()

    def get_first_in_line(self, line_number: int) -> Optional[Customer]:
        """ Повернути першого клієнта в черзі <line_number> або None, якщо в черзі немає клієнтів.
        """
        line = self._checkout_lines[line_number]
        if len(line) == 0:
            return None
        else:
            return line.queue[0]


class Customer:
    """
    Покупець продуктового магазину.

    Атрибути
    name:  унікальний ідентифікатор для цього клієнта.
    arrival_time: час, коли цей клієнт приєднався до черги.
    _items: елементи, які має цей клієнт.

    Інваріант подання 
    arrival_time >= 0, якщо цей клієнт приєднався до черги, і -1 в іншому випадку
    """
    name: str
    arrival_time: int
    _items: List[Item]

    def __init__(self, name: str, items: List[Item]) -> None:
        """Ініціалізація клієнта заданим ім`ям, початковим часом прибуття
        """
        self.name = name
        self.arrival_time = -1
        self._items = items

    def num_items(self) -> int:
        """Повертає кількість елементів, які має цей клієнт.
        """
        return len(self._items)

    def get_item_time(self) -> int:
        """Повертає кількість секунд, необхідних для перевірки цього клієнта.
        """
        time = 0
        for item in self._items:
            time += item.get_time()
        return time


class Item:
    """Клас для представлення елемента, який потрібно перевірити.

     Не змінюйте цей клас.

     Атрибути
     name: назва цього елемента
     _time: час, необхідний для оформлення цього товару
    """
    name: str
    _time: int

    def __init__(self, name: str, time: int) -> None:
        """Ініціалізуйте новий час за допомогою назві та часу.
        """
        self.name = name
        self._time = time

    def get_time(self) -> int:
        """Поверніть, скільки секунд потрібно, щоб отримати цей товар.
        """
        return self._time


class CheckoutLine:
    """Черга до каси в продуктовому магазині.

     Це абстрактний клас; підкласи відповідають за реалізацію
     start_checkout().

     === Атрибути ===
     capacity: дозволена кількість клієнтів у цій касовій лінії.
     is_open: Правда, якщо лінія відкрита.
     queue: клієнти в цьому рядку в порядку FIFO.

     Інваріанти подання
     - Кожен клієнт у цій лінії ще не перевірений.
     - Кількість клієнтів менше або дорівнює потужності.
    """
    capacity: int
    is_open: bool
    queue: List[Customer]

    def __init__(self, capacity: int) -> None:
        """Ініціалізація відкритого і порожнього рядка каси.
        """
        self.capacity = capacity
        self.is_open = True
        self.queue = []

    def __len__(self) -> int:
        """Повертає розмір цього CheckoutLine.
        """
        return len(self.queue)

    def can_accept(self, customer: Customer) -> bool:
        """
        Повертає True, якщо цей CheckoutLine може прийняти <customer>.
        """
        if len(self) < self.capacity and self.is_open:
            return True
        else:
            return False

    def accept(self, customer: Customer) -> bool:
        """Прийміть покупця у кінці цієї каси.
         Повертає True, якщо клієнта прийнято.
        """
        if self.can_accept(customer):
            self.queue.append(customer)
            return True
        else:
            return False

    def start_checkout(self) -> int:
        """Перевірка наступного клієнта в цьому рядку CheckoutLine.

         Повернення часу, який знадобиться для оплати наступного клієнта.
        """
        return self.queue[0].get_item_time()

    def complete_checkout(self) -> bool:
        """Завершення оформлення замовлення для цієї каси.

         Повідомляє, чи залишилися клієнти в черзі.
        """
        self.queue.pop(0)
        if len(self.queue) > 0:
            return True
        else:
            return False

    def close(self) -> List[Customer]:
        """Закриття цього рядка.

        Повернення списку усіх клієнтів, яких потрібно перемістити на інший рядок.
        """
        self.is_open = False
        remaining = self.queue[1:]
        self.queue = self.queue[:1]
        return remaining


class RegularLine(CheckoutLine):
    """Звичайна каса."""


class ExpressLine(CheckoutLine):
    """Експрес-каса
    """
    def can_accept(self, customer: Customer) -> bool:
        """Повертає True, якщо каса може прийняти покупця
        """
        if len(self) < self.capacity and customer.num_items() <= EXPRESS_LIMIT \
           and self.is_open:
            return True
        else:
            return False


class SelfServeLine(CheckoutLine):
    """ Каса самообслуговування
    """
    def start_checkout(self) -> int:
        """Перевітка наступного клієнта в цьому рядку CheckoutLine.

         Повернення часу, який знадобиться для оплати наступного клієнта.
        """
        return self.queue[0].get_item_time() * 2


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': ['__future__', 'typing', 'json',
                                   'python_ta', 'doctest'],
        'disable': ['W0613']})
