# aioboto3 mocking with Pytest and Moto

This project demonstrates how to set up a Moto background service and patch the aioboto3 session to forward all calls to it. This is designed to work against any calls that create an `aiobotocore3.Session()` or `botocore3.Session()` automatically. This means you should not have to change any implementation code for how you are managing the aioboto3 `Session`.

Most of the code for this came from the aioboto3 tests themselves at https://github.com/terrycain/aioboto3/blob/92a7a9b8a32615ab6a9ea51ef360475ede94bb1f/tests/mock_server.py. Divergence in this gist:

- Only initializes a moto server for S3
- Includes a sustainable pattern for adding additional AWS mocked services
- Fully type-hinted

## Running the example test

- Poetry 1.1+
- Python 3.9+ (although probably Python 3.7+ will work)

```
poetry install
poetry run pytest
```

Example output:

```console
================================================================================================= test session starts =================================================================================================
platform darwin -- Python 3.9.11, pytest-7.1.2, pluggy-1.0.0
rootdir: /Users/phillip/aioboto3-testing, configfile: pyproject.toml, testpaths: tests
plugins: asyncio-0.18.3
asyncio: mode=auto
collected 1 item

tests/test_s3.py .                                                                                                                                                                                              [100%]

================================================================================================== 1 passed in 0.96s ==================================================================================================
```

## Intended Usage

1. Copy in `tests/aioboto3_fixtures` and `tests/moto_fixtures.py` into your project
2. Ensure that your root `conftest.py` includes these as plugins:
    ```python
    pytest_plugins = [
        "path.to.moto_fixtures",
        "path.to.aioboto3_fixtures",
    ]
    ```
3. Inject the included `aioboto3_s3_client` fixture:
    ```python
    async def test_aio_aws_bucket_access(aioboto3_s3_client: S3Client) -> None:
        resp = await aioboto3_s3_client.list_buckets()
        ...
    ```
    or create a new `Session` yourself by injecting the `moto_patch_session` fixture:
    ```python
    async def test_some_s3_thing(moto_patch_session: None) -> None:
        session = aioboto3.Session(region_name="us-east-1")
        async with session.client("s3", region_name="us-east-1") as client:  # type: S3Client
            yield client
    ```