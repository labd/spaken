import os
from urllib.parse import urlparse
from botocore.exceptions import BotoCoreError, ClientError

import boto3

from spaken.exceptions import StorageException


class S3Storage:

    def __init__(self, uri):
        bucket_name, bucket_path = parse_bucket_uri(uri)
        s3 = boto3.resource('s3')
        try:
            s3.meta.client.head_bucket(Bucket=bucket_name)
        except (BotoCoreError, ClientError) as exc:
            raise StorageException(str(exc))

        self._bucket = s3.Bucket(bucket_name)
        self._path = bucket_path

    def list_files(self):
        if self._path:
            objects = self._bucket.objects.filter(Prefix=self._path)
        else:
            objects = self._bucket.objects.all()

        return [os.path.relpath(obj.key, self._path) for obj in objects]

    def upload(self, source, filename):
        key = self._path + filename
        with open(source, 'rb') as fh:
            self._bucket.put_object(Key=key, Body=fh.read())

    def get(self, filename, destination):
        key = self._path + filename
        self._bucket.download_file(key, destination)


def parse_bucket_uri(uri):
    result = urlparse(uri)

    path = result.path
    if path:
        path = path[1:]
    if not path.endswith('/'):
        path += '/'

    # Remove leading /
    path = path.lstrip('/')
    return result.netloc, path
