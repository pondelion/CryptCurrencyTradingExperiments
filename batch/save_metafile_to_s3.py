from datetime import datetime, timedelta
import glob
import os
import sys
import time
sys.path.append('..')


from src.storage.s3 import S3


S3_SAVE_DIR = 's3://finapp-crypto-currency/board_image/meta'


csv_files = glob.glob('../metafile/*/*.csv')
print(csv_files)
# csv_files = list(filter(
#     lambda x: datetime.today().strftime("%Y%m%d"),
#     csv_files
# ))

for f in csv_files:
    s3_filepath = os.path.join(
        S3_SAVE_DIR,
        f.split('/')[-2],
        f.split('/')[-1]
    )
    S3.save_file(
        f,
        s3_filepath
    )
    print(f'Saved to {s3_filepath}')


