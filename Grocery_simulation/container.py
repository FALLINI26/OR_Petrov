"""
Цей модуль містить класи, що представляють контейнер
і типи даних пріоритетної черги.

"""

from __future__ import annotations
from typing import Any, List


class Container:
    """
    Контейнер, який містить об’єкти.
    Це абстрактний клас. Тільки дочірні класи повинні бути створені.

    """

    def add(self, item: Any) -> None:
        """Додає <item> до цього контейнера.
        """
        raise NotImplementedError('Implemented in a subclass')

    def remove(self) -> None:
        """Видалення і повернення одного предмета із цього контейнера.
        """
        raise NotImplementedError('Implemented in a subclass')

    def is_empty(self) -> bool:
        """Повертання True, якщо цей контейнер порожній.
        """
        raise NotImplementedError('Implemented in a subclass')


class PriorityQueue(Container):
    """Черга елементів, яка працює в пріоритетному порядку.

    Предмети видаляються з черги відповідно до пріоритету; елемент з
    найвищий пріоритет видаляється першим. Нічия вирішується в порядку FIFO,
    тобто елемент, який був вставлений *раніше*, є першим
    видалено.

    Пріоритет визначається багатими методами порівняння для об’єктів у
    контейнер (__lt__, __le__, __gt__, __ge__).

    Якщо x < y, то x має *ВИЩИЙ* пріоритет, ніж y.

    Усі об’єкти в контейнері мають бути одного типу.

    === Приватні атрибути ===
    _items: елементи, що зберігаються в черзі пріоритету.

    === Інваріанти подання ===
    _items — це відсортований список, де першим є елемент із
     найвищий пріоритет.
    """
    _items: List

    def __init__(self) -> None:
        """Ініціалізування порожної черги PriorityQueue.
        """
        self._items = []

    def remove(self) -> Any:
        """Видалення та повернення наступного елемента із цієї черги пріоритетів.

         Передумова: <self> не має бути порожнім.
        """
        return self._items.pop(0)

    def is_empty(self) -> bool:
        """
        Повертає True, якщо ця PriorityQueue порожня.

        """
        return len(self._items) == 0

    def add(self, item: Any) -> None:
        """Додавання <item> до цієї черги PriorityQueue

        """
        temp_items = self._items.copy()
        if not self._items:
            self._items.append(item)
            return None
        else:
            for element in temp_items:
                if item < element:
                    self._items.insert(self._items.index(element), item)
                    return None
            self._items.append(item)
            return None


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': ['__future__', 'typing',
                                   'python_ta', 'doctest']})
