import pytest

import boto3
from moto import mock_s3


@pytest.fixture(scope='function')
def s3_storage():
    with mock_s3():
        conn = boto3.resource('s3', region_name='eu-west-1')
        conn.create_bucket(Bucket='spaken-test')
        yield {'bucket': 'spaken-test'}
