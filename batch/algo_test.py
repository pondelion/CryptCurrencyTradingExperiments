import time
import sys
sys.path.append('..')

from src.entity.price import (
    Price,
    ProductCode
)
from src.algos.a1 import A1
from src.notifier.sqs import (
    SQSPolling,
    SlackMessage
)


sqs = SQSPolling()

a = A1(init_cash=500000)
a.run()

i = 0

while True:
    print(a)
    print(a.asset)
    time.sleep(5)
    if i % 20 == 0:
        sqs.push_message(
            message=SlackMessage(
                # channel='crypt_curreny',
                channel='finapp',
                message=f'asset : {a.asset}'
            )
        )
    i += 1
