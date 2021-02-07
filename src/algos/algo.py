from abc import ABCMeta, abstractmethod
import threading

from ..entity.price import (
    Price,
    ProductCode
)


class Algo(metaclass=ABCMeta):

    def __init__(
        self,
        init_cash: int,
        init_btc: float = 0.0,
        transaction_cost: int = 0
    ):
        self._cash = init_cash
        self._btc = init_btc
        self._running = True
        self._transaction_cost = transaction_cost

    def run(self):
        self._running = True
        threading.Thread(target=self._run).start()

    @abstractmethod
    def _run(self):
        raise NotImplementedError

    @property
    def cash(self):
        return self._cash

    @property
    def asset(self):
        p = Price.latest(ProductCode.BTC_JPY)[0]
        return self._cash + p['ltp']*self._btc

    def stop(self):
        self._running = False

    def __str__(self):
        return f'cash : {self._cash}, btc : {self._btc}'
