"""
Цей модуль містить усі класи, необхідні для моделювання різних видів подій у дослідженні.

"""
from __future__ import annotations
from typing import List, TextIO
from store import Customer, Item


class Event:
    """Подія.

    Події впорядковуються на основі мітки часу події без зростання
    порядок. Подій зі старішими мітками часу більше, ніж подій із новішими
    позначки часу.

    Цей клас є абстрактним; підкласи повинні реалізовувати do().

    Атрибути-timestamp: мітка часу для цієї події.
    """
    timestamp: int

    def __init__(self, timestamp: int) -> None:
        """Ініціалізація події з заданою міткою часу.

        Передумова: позначка часу має бути невід’ємним цілим числом.

        """
        self.timestamp = timestamp

    def __eq__(self, other: Event) -> bool:
        """Повертає, чи дорівнює ця подія <other>.

        Дві події є рівними, якщо вони мають однакову позначку часу.

        """
        return self.timestamp == other.timestamp

    def __ne__(self, other: Event) -> bool:
        """Повертає True, якщо ця подія не дорівнює <other>.

        """
        return not self.__eq__(other)

    def __lt__(self, other: Event) -> bool:
        """Повертає True, якщо ця подія менша за <other>.

        """
        return self.timestamp < other.timestamp

    def __le__(self, other: Event) -> bool:
        """Повертає True, якщо ця подія менше або дорівнює <other>.

        """
        return self.timestamp <= other.timestamp

    def __gt__(self, other: Event) -> bool:
        """Повертає True, якщо ця подія більша за <other>.

        """
        return not self.__le__(other)

    def __ge__(self, other: Event) -> bool:
        """Повертає True, якщо ця подія більше або дорівнює <other>.
        """
        return not self.__lt__(other)

    def do(self, store: "GroceryStore") -> List[Event]:
        """Повертає список подій, згенерованих виконанням цієї події.

        Викликати методи в <store>, щоб оновити його стан відповідно до
        значення події. Примітка: «бізнес-логіка» чого насправді
        що трапляється в продуктовому магазині, слід розглядати в GroceryStore
        класі, а не в будь-яких класах подій.

        Повернути список нових подій, породжених цією подією (переконавшись, що
        мітки часу правильні).
        """
        raise NotImplementedError('Implemented in a subclass')


class CustomerArrival(Event):
    """Клієнт приходить до каси, готовий починати оплату.
     клієнт: клієнт, що прибуває
    """
    customer: Customer

    def __init__(self, timestamp: int, c: Customer) -> None:
        """ Ініціалізуйте подію CustomerArrival за допомогою <timestamp> і клієнта <c>.
        """
        Event.__init__(self, timestamp)
        self.customer = c

    def do(self, store: "GroceryStore") -> List[Event]:
        """ Призначає прибулого клієнта до черги в <store>.
        """
        line_number = store.enter_line(self.customer)
        self.customer.arrival_time = self.timestamp
        if line_number == -1:
            return [CustomerArrival(self.timestamp + 1, self.customer)]
        if store.line_is_ready(line_number):
            return [CheckoutStarted(self.timestamp, line_number)]
        else:
            return []

    def __str__(self) -> str:
        """ Повертає рядок Представлення об'єкта
        """
        return self.customer.name + ' arrives at ' + str(self.timestamp)


class CheckoutStarted(Event):
    """Клієнт починає процес оформлення замовлення.

     Щойно процес оформлення почнеться, це єдиний спосіб для клієнта вийти
     рядок призначений для події CheckoutCompleted.

     Атрибути-line_number: номер касового рядка.
    """
    line_number: int

    def __init__(self, timestamp: int, line_number: int) -> None:
        """Ініціалізування події CheckoutStarted за допомогою <timestamp> і
         <номер_рядка>.
        """
        Event.__init__(self, timestamp)
        self.line_number = line_number

    def do(self, store: "GroceryStore") -> List[Event]:
        """Починає перевірку для наступного клієнта в line_number.
        """
        billing_time = store.start_checkout(self.line_number)
        return [CheckoutCompleted(self.timestamp + billing_time,
                                  self.line_number,
                                  store.get_first_in_line(self.line_number))]

    def __str__(self) -> str:
        """Повертає рядок Представлення об'єкта
        """
        return 'Checkout started at ' + str(self.timestamp) + \
               ' on line ' + str(self.line_number)


class CheckoutCompleted(Event):
    """Клієнт завершує процес оформлення замовлення.

     Подія CheckoutCompleted може статися після закриття лінії.

     Атрибути-line_number: номер касового рядка.
     замовник-Замовник обробки.
    """
    line_number: int
    customer: Customer

    def __init__(self, timestamp: int, line_number: int, c: Customer) -> None:
        """Ініціалізація події CheckoutCompleted за допомогою <timestamp>, <line_number>, і клієнта <c>.
        """
        Event.__init__(self, timestamp)
        self.line_number = line_number
        self.customer = c

    def do(self, store: "GroceryStore") -> List[Event]:
        """Завершує оформлення замовлення для клієнта в номері рядка.
        """
        are_more = store.complete_checkout(self.line_number)
        if are_more:
            return [CheckoutStarted(self.timestamp, self.line_number)]
        else:
            return []

    def __str__(self) -> str:
        """ Повертає рядок Представлення об'єкта
        """
        return self.customer.name + ' completes checkout at ' + \
               str(self.timestamp) + ' line ' + str(self.line_number)


class CloseLine(Event):
    """CheckoutLine закривається.

     Атрибути-line_number: номер касового рядка.
    """
    line_number: int

    def __init__(self, timestamp: int, line_number: int) -> None:
        """Ініціалізування подію CloseLine за допомогою <timestamp> і <line_number>.
        """
        Event.__init__(self, timestamp)
        self.line_number = line_number

    def do(self, store: "GroceryStore") -> List[Event]:
        """Закриває рядок line_number і повертає події new customer.
        """
        remaining_customers = store.close_line(self.line_number)[::-1]
        new_events = []
        for customer in remaining_customers:
            new_events.append(CustomerArrival(self.timestamp, customer))
            self.timestamp += 1
        return new_events

    def __str__(self) -> str:
        """ Повертає рядок Представлення об'єкта
        """
        return 'Line ' + str(self.line_number) + \
               ' closed at ' + str(self.timestamp)


def create_event_list(event_file: TextIO) -> List[Event]:
    """Повертає список подій на основі необробленого списку подій у <event_file>.
    """
    file = [event.strip('\n').split() for event in event_file]
    events = []
    for line in file:
        if line[1] == 'Arrive':
            time = int(line[0])
            customer_name = line[2]
            items = []
            i = 3
            while i < len(line):
                items.append(Item(line[i], int(line[i+1])))
                i += 2
            events.append(CustomerArrival(time, Customer(customer_name, items)))
        else:
            time = int(line[0])
            line_index = int(line[2])
            events.append(CloseLine(time, line_index))
    return events


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': ['__future__', 'typing', 'store',
                                   'python_ta', 'doctest']})
