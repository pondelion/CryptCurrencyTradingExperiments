import requests
import time
import threading
from datetime import datetime
from pytz import timezone

from ..db.sqlite import (
    get_db_conn,
    execute_commit
)
from ..entity.price import ProductCode


_crawling = False
INTERVAL_SEC = 5
DB_TABLE_NAME = 'bitflyer'
BF_TABLE_CREATE_SQL = f"""
CREATE TABLE IF NOT EXISTS {DB_TABLE_NAME} (
    id INTEGER PRIMARY KEY AUTOINCREMENT
    , timestamp TIMESTAMP
    , tick_id INTEGER
    , product_code TEXT
    , best_bid REAL
    , best_ask REAL
    , best_bid_size REAL
    , best_ask_size REAL
    , ltp REAL
    , volume REAL
    , created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime'))
)
"""
DB_CONN = get_db_conn()
execute_commit(BF_TABLE_CREATE_SQL)


INSERT_SQL = f"""
INSERT INTO {DB_TABLE_NAME}(
    timestamp,
    tick_id,
    product_code,
    best_bid,
    best_ask,
    best_bid_size,
    best_ask_size,
    ltp,
    volume
) values(
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?
)
"""

COLUMNS = [
    'timestamp', 'tick_id', 'product_code', 'best_bid', 'best_ask', 'best_bid_size', 'best_ask_size', 'ltp', 'volume'
]

def crawl_worker(product_code: ProductCode = ProductCode.BTC_JPY):
    URL = f'https://api.bitflyer.com/v1/ticker?product_code={product_code.value}'
    print(f'start crawling bitflyer : {product_code}')
    global _crawling
    _crawling = True
    while _crawling:
        try:
            res = requests.get(URL)
            data = res.json()
            print(data)
            data['timestamp'] = datetime.strptime(data['timestamp'], '%Y-%m-%dT%H:%M:%S.%f').timestamp()
            args = [data[col_name] for col_name in COLUMNS]
            execute_commit(INSERT_SQL, args)
        except Exception as e:
            print(e)
            if 'API limit' in data.get('error_message', ''):
                print(data.get('error_message', ''))
                print('waiting 60 sec')
            time.sleep(60)
        time.sleep(INTERVAL_SEC)
    print('end crawling bitflyer')


def start_crawl():
    if _crawling:
        return
    PRODUCT_CODES = [ProductCode.BTC_JPY, ProductCode.ETH_JPY, ProductCode.BCH_BTC]
    for pc in PRODUCT_CODES:
        t = threading.Thread(target=crawl_worker, args=(pc,))
        t.start()


def end_crawl():
    global _crawling
    _crawling = False
