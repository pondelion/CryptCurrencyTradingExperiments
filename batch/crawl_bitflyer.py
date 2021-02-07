import time
import sys
sys.path.append('..')

from src.crawl.bitflyer import (
    start_crawl,
    end_crawl
)


start_crawl()
while True:
    time.sleep(60)
