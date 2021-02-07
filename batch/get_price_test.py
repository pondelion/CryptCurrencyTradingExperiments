import time
import sys
sys.path.append('..')

from src.entity.price import (
    Price,
    ProductCode
)


p = Price.latest(ProductCode.BTC_JPY)
print(p)
