import concurrent
import decimal
import json
from unittest.mock import MagicMock, patch

import pytest
from google.cloud.pubsub_v1 import PublisherClient
from google.cloud.pubsub_v1.exceptions import TimeoutError
from google.protobuf import timestamp_pb2

from rele import Publisher
from rele.client import Subscriber
from rele.config import Config
from rele.middleware import register_middleware
from rele.retry_policy import RetryPolicy


@pytest.fixture
def project_id():
    return "rele-test"


@pytest.fixture
def config(project_id):
    return Config(
        {
            "APP_NAME": "rele",
            "SUB_PREFIX": "rele",
            "GC_CREDENTIALS_PATH": "tests/dummy-pub-sub-credentials.json",
            "GC_STORAGE_REGION": "some-region",
            "MIDDLEWARE": ["rele.contrib.LoggingMiddleware"],
        }
    )


@pytest.fixture
def config_with_retry_policy(project_id):
    return Config(
        {
            "APP_NAME": "rele",
            "SUB_PREFIX": "rele",
            "GC_CREDENTIALS_PATH": "tests/dummy-pub-sub-credentials.json",
            "GC_STORAGE_REGION": "some-region",
            "MIDDLEWARE": ["rele.contrib.LoggingMiddleware"],
            "DEFAULT_RETRY_POLICY": RetryPolicy(5, 30),
        }
    )


@pytest.fixture
def subscriber(project_id, config):
    return Subscriber(
        config.gc_project_id, config.credentials, config.gc_storage_region, 60
    )


@pytest.fixture
def mock_future():
    return MagicMock(spec=concurrent.futures.Future)


@pytest.fixture
def publisher(config, mock_future):
    publisher = Publisher(
        gc_project_id=config.gc_project_id,
        credentials=config.credentials,
        encoder=config.encoder,
        timeout=config.publisher_timeout,
        blocking=config.publisher_blocking,
    )
    publisher._client = MagicMock(spec=PublisherClient)
    publisher._client.publish.return_value = mock_future

    return publisher


@pytest.fixture
def published_at():
    return 1560244246.863829


@pytest.fixture
def time_mock(published_at):
    with patch("time.time") as mock:
        mock.return_value = published_at
        yield mock


@pytest.fixture(autouse=True)
def default_middleware(config):
    register_middleware(config=config)


@pytest.fixture
def custom_encoder():
    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, decimal.Decimal):
                return float(obj)

    return DecimalEncoder


@pytest.fixture
def mock_publish_timeout():
    with patch("rele.client.Publisher.publish") as mock:
        mock.side_effect = TimeoutError()
        yield mock


@pytest.fixture
def mock_post_publish_failure():
    with patch(
        "rele.contrib.logging_middleware.LoggingMiddleware.post_publish_failure"
    ) as mock:
        yield mock


@pytest.fixture
def publish_time():
    timestamp = timestamp_pb2.Timestamp()
    timestamp.GetCurrentTime()
    return timestamp
