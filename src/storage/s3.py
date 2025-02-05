import os
from typing import List

from .base_storage import BaseStorage
from ..aws_resource import S3 as S3_resource


DEFAULT_BUCKET_NAME = 'finapp-crypto-currency'


class S3(BaseStorage):

    @staticmethod
    def save_file(
        local_filepath: str,
        s3_filepath: str,
        bucket_name: str = DEFAULT_BUCKET_NAME,
    ) -> None:
        bucket = S3_resource.Bucket(bucket_name)

        if s3_filepath.startswith('s3://'):
            s3_filepath = s3_filepath.replace(f's3://{bucket_name}/', '')

        bucket.upload_file(
            local_filepath,
            s3_filepath
        )

    @staticmethod
    def get_filelist(
        basedir: str,
        bucket_name: str = DEFAULT_BUCKET_NAME,
        marker: str = '',
    ) -> List[str]:
        bucket = S3_resource.Bucket(bucket_name)
        objs = bucket.meta.client.list_objects(
            Bucket=bucket.name,
            Prefix=basedir if basedir[-1] == '/' else basedir + '/',
            Marker=marker,
        )

        s3_prefix = f's3://{bucket_name}/'
        s3_filelist = []

        while 'Contents' in objs:
            files = [o.get('Key') for o in objs.get('Contents')]

            s3_paths = [os.path.join(
                s3_prefix,
                file,
            ) for file in files]

            s3_filelist += s3_paths

            if 'IsTruncated' in objs:
                marker = files[-1]
                objs = bucket.meta.client.list_objects(
                    Bucket=bucket.name,
                    Prefix=basedir if basedir[-1] == '/' else basedir + '/',
                    Marker=marker,
                )
            else:
                break

        return s3_filelist

    @staticmethod
    def download_file(
        s3_filepath: str,
        local_filepath: str,
        bucket_name: str = DEFAULT_BUCKET_NAME,
    ) -> str:
        bucket = S3_resource.Bucket(bucket_name)

        s3_prefix = f's3://{bucket_name}/'
        filepath = s3_filepath.replace(s3_prefix, '')
        object = bucket.Object(filepath)
        object.download_file(local_filepath)

        return local_filepath
