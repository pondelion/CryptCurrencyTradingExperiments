import json
from time import sleep
import os
from datetime import datetime

import websocket
import matplotlib.pyplot as plt
import pandas as pd

from ..storage.s3 import S3


class CSVMetaFile:

    def __init__(self, product_code: str):
        self._COL_NAMES = ['datetime', 'mid_price', 's3_image_filepath']
        self._product_code = product_code
        self._save_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../../metafile',
            self._product_code
        )
        os.makedirs(self._save_dir, exist_ok=True)
        self._filepath = self.get_filename()
        self._df_meta = self._load_or_create(self._filepath)

    def get_filename(self):
        return os.path.join(
            self._save_dir,
            f'{datetime.now().strftime("%Y%m%d")}.csv'
        )

    def _load_or_create(self, filepath: str) -> pd.DataFrame:
        if os.path.exists(filepath):
            return pd.read_csv(filepath)
        else:
            return pd.DataFrame(columns=self._COL_NAMES)

    def append(self, dt: datetime, mid_price: float, s3_filepath: str):
        data = pd.Series([dt, mid_price, s3_filepath], index=self._COL_NAMES)
        if self._filepath == self.get_filename():
            self._df_meta = self._df_meta.append(data, ignore_index=True)
            self._df_meta.to_csv(self._filepath, index=False)
        else:
            self._filepath = self.get_filename()
            self._df_meta = self._load_or_create(self._filepath)
            self._df_meta = self._df_meta.append(data, ignore_index=True)
            self._df_meta.to_csv(self._filepath, index=False)


class RealtimeAPI(object):

    def __init__(self, product_code: str = 'BTC_JPY'):
        self.url = 'wss://ws.lightstream.bitflyer.com/json-rpc'
        self.channel = f'lightning_board_snapshot_{product_code}'
        self._csv_metafile = CSVMetaFile(product_code)
        self._product_code = product_code

        self.ws = websocket.WebSocketApp(
            self.url,
            header=None,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        websocket.enableTrace(True)

    def run(self):
        self.ws.run_forever()

    def on_message(self, ws, message):
        # print('on_message')
        timestamp = datetime.now()
        data = json.loads(message)['params']
        #print(json.dumps(data, indent=2))
        prices = [d['price'] for d in data['message']['bids']]
        prices += [d['price'] for d in data['message']['asks']]
        sizes = [d['size'] for d in data['message']['bids']]
        sizes += [-d['size'] for d in data['message']['asks']]
        plt.rcParams["axes.facecolor"] = (1,1,1,0)
        plt.figure(figsize=(6, 6), facecolor='black')
        plt.tick_params(
            bottom=False,
            left=False,
            right=False,
            top=False
        )
        plt.tick_params(
            labelbottom=False,
            labelleft=False,
            labelright=False,
            labeltop=False
        )
        height = 3*(max(prices)-min(prices))/len(prices)
        plt.barh(prices, sizes, height=height, color="white")
        local_image_filepath = 'tmp.png'
        plt.savefig(local_image_filepath, bbox_inches="tight", pad_inches=0.0)
        # plt.savefig('test.png', pad_inches=0.0)
        plt.close()
        plt.clf()

        s3_filepath = f's3://finapp-crypto-currency/board_image/{self._product_code}/{timestamp.strftime("%Y%m%d_%H%M%S")}.png'
        S3.save_file(
            local_image_filepath,
            s3_filepath
        )
        self._csv_metafile.append(
            dt=datetime.now(),
            mid_price=data['message']['mid_price'],
            s3_filepath=s3_filepath
        )
        print(f'Saved to {s3_filepath}')

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print('on_close')

    def on_open(self, ws):
        print('on_open')
        data = json.dumps({
            'method' : 'subscribe',
            'params' : {'channel': self.channel}
        })
        ws.send(data)


def start_crawl():
    while True:
        realtime_api = RealtimeAPI()
        realtime_api.run()
        time.sleep(10)
