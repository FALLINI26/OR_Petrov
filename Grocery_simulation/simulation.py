"""
Цей модуль містить клас для імітації продуктового магазину, а також приклад коду тестування.

"""
from __future__ import annotations
from typing import Dict, Any, TextIO
from event import create_event_list, CustomerArrival, CheckoutCompleted
from store import GroceryStore
from container import PriorityQueue


class GroceryStoreSimulation:
    """
    Симуляція продуктового магазину.

     Це клас, який відповідає за встановлення та запуск a
     моделювання. 

     Приватні атрибути 
     _events: послідовність подій, упорядкованих за пріоритетом, визначеним подією
              порядок сортування.
     _store: магазин, що моделюється.
    """
    _events: PriorityQueue
    _store: GroceryStore

    def __init__(self, store_file: TextIO) -> None:
        """Ініціалізація GroceryStoreSimulation за допомогою конфігурації <store_file>.
        """
        self._events = PriorityQueue()
        self._store = GroceryStore(store_file)

    def run(self, file: TextIO) -> Dict[str, Any]:
        """Запустіть симуляцію подій, збережених у <initial_events>.

         Повертає словник, що містить статистику дослідження
        """
        #Ініціалізація статистики
        stats = {
            'num_customers': 0,
            'total_time': 0,
            'max_wait': -1
        }
        max_waits = dict()
        initial_event_list = create_event_list(file)

        for event in initial_event_list:
            self._events.add(event)
            if isinstance(event, CustomerArrival):
                stats['num_customers'] += 1
                max_waits[event.customer] = event.timestamp

        while not self._events.is_empty():
            event = self._events.remove()
            if isinstance(event, CheckoutCompleted):
                max_waits[event.customer] = event.timestamp -   \
                                            max_waits[event.customer]
            spawns = event.do(self._store)
            for spawn in spawns:
                self._events.add(spawn)
            stats['total_time'] = event.timestamp

        stats['max_wait'] = max_waits[max(max_waits, key=max_waits.get)]
        return stats


if __name__ == '__main__':
    config_file = open('input_files/config_Petrov.json')
    sim = GroceryStoreSimulation(config_file)
    config_file.close()
    event_file = open('input_files/events_mixtures.txt')
    sim_stats = sim.run(event_file)
    event_file.close()
    print(sim_stats)
    import doctest
    doctest.testmod()
