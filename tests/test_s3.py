import pytest
from types_aiobotocore_s3 import S3Client


@pytest.fixture
def aio_s3_bucket_name() -> str:
    return "aio_moto_bucket"


def assert_status_code(response, status_code):
    assert response.get("ResponseMetadata", {}).get("HTTPStatusCode") == status_code


def response_success(response):
    return response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200


@pytest.fixture
async def aio_s3_bucket(aio_s3_bucket_name, aioboto3_s3_client: S3Client) -> str:
    resp = await aioboto3_s3_client.create_bucket(Bucket=aio_s3_bucket_name)
    assert response_success(resp)
    head = await aioboto3_s3_client.head_bucket(Bucket=aio_s3_bucket_name)
    assert response_success(head)
    return aio_s3_bucket_name


async def test_aio_aws_bucket_access(aioboto3_s3_client: S3Client, aio_s3_bucket) -> None:
    resp = await aioboto3_s3_client.list_buckets()
    assert response_success(resp)
    bucket_names = [b["Name"] for b in resp["Buckets"]]
    assert bucket_names == [aio_s3_bucket]
