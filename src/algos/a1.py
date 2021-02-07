import time
import random
import threading

from ..entity.price import (
    Price,
    ProductCode
)
from .algo import Algo


class A1(Algo):

    def _run(self):
        while self._running:
            p = Price.latest(ProductCode.BTC_JPY)[0]
            MAX_SIZE = 0.01
            size = random.random()*MAX_SIZE
            if size > 0 and self._cash >= size*p['ltp']:
                self._btc += size
                self._cash -= size*p['ltp'] - self._transaction_cost
                print(f'buy : btc size => {size}')
            elif size < 0 and self._btc >= size:
                self._btc -= size
                self._cash += size*p['ltp'] - self._transaction_cost
                print(f'sell : btc size => {size}')

            time.sleep(random.randint(2, 30))