import time
from enum import Enum

from ..db.sqlite import execute_commit


SELECT_LATEST_SQL = """
SELECT
  ltp, timestamp
FROM
  bitflyer
WHERE
  product_code = ? AND
  timestamp = (select MAX(timestamp) from bitflyer where product_code = ?)
"""

MAX_RETRY = 4


class ProductCode(Enum):
    BTC_JPY = 'BTC_JPY'
    ETH_JPY = 'ETH_JPY'
    BCH_BTC = 'BCH_BTC'


class Price:

    @staticmethod
    def latest(product_code: ProductCode = ProductCode.BTC_JPY):
        retry = 0
        while retry <= MAX_RETRY:
            try:
                res = execute_commit(SELECT_LATEST_SQL, (product_code.value, product_code.value))
                res = [{'ltp': v[0], 'timestamp': v[1]} for v in res]
                break
            except Exception as e:
                print(e)
                retry += 1
        return res
