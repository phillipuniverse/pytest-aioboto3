# aioboto3 mocking with Pytest and Moto

This is a Pytest plugin that sets up a Moto background service and patch the aioboto3 session to forward all calls to it. This is designed to work against any calls that create an `aiobotocore3.Session()` or `botocore3.Session()` automatically. This means you should not have to change any implementation code for how you are managing the aioboto3 `Session`.

Most of the code for this came from the aioboto3 tests themselves at https://github.com/terrycain/aioboto3/blob/92a7a9b8a32615ab6a9ea51ef360475ede94bb1f/tests/mock_server.py. Divergence in this gist:

- Only initializes a moto server for S3
- Includes a sustainable pattern for adding additional AWS mocked services
- Fully type-hinted

## Running the example test

- Poetry 1.6+
- Python 3.10+ (although probably Python 3.7+ will work)

```
poetry install
poetry run pytest
```

Example output:

```console
=========================================================================================================== test session starts ===========================================================================================================
platform darwin -- Python 3.11.6, pytest-7.4.3, pluggy-1.3.0
rootdir: /Users/phillip/pytest-aioboto3
configfile: pyproject.toml
testpaths: tests
plugins: asyncio-0.21.1, aioboto3-0.1.0
asyncio: mode=Mode.AUTO
collected 1 item

tests/test_s3.py .                                                                                                                                                                                                                  [100%]

============================================================================================================ 1 passed in 0.94s ============================================================================================================
```

## Installation

`pip install pytest-aioboto3`

## Usage

Inject the included `aioboto3_s3_client` fixture:
```python
async def test_aio_aws_bucket_access(aioboto3_s3_client: S3Client) -> None:
    resp = await aioboto3_s3_client.list_buckets()
    ...
```

Or create a new `Session` yourself by injecting the `moto_patch_session` fixture:
```python
async def test_some_s3_thing(moto_patch_session: None) -> None:
    session = aioboto3.Session(region_name="us-east-1")
    async with session.client("s3", region_name="us-east-1") as client:  # type: S3Client
        yield client
```
