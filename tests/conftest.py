import concurrent
import decimal
import json
from unittest.mock import MagicMock, patch

import pytest
from google.cloud.pubsub_v1 import PublisherClient
from google.oauth2 import service_account

from rele import Publisher
from rele.client import Subscriber
from rele.config import Config
from rele.middleware import register_middleware


@pytest.fixture
def project_id():
    return "rele-test"


@pytest.fixture
def credentials():
    return service_account.Credentials.from_service_account_file(
        "tests/dummy-pub-sub-credentials.json"
    )


@pytest.fixture
def config(credentials, project_id):
    return Config(
        {
            "APP_NAME": "rele",
            "SUB_PREFIX": "rele",
            "GC_PROJECT_ID": project_id,
            "GC_CREDENTIALS": credentials,
            "MIDDLEWARE": ["rele.contrib.LoggingMiddleware"],
        }
    )


@pytest.fixture
def subscriber(project_id, credentials):
    return Subscriber(project_id, credentials, 60)


@pytest.fixture
def publisher(config):
    publisher = Publisher(
        gc_project_id=config.gc_project_id,
        credentials=config.credentials,
        encoder=config.encoder,
        timeout=config.publisher_timeout,
    )
    publisher._client = MagicMock(spec=PublisherClient)
    publisher._client.publish.return_value = concurrent.futures.Future()

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
def mock_post_process_message_failure():
    with patch("rele.middleware.BaseMiddleware.post_process_message_failure") as mock:
        yield mock
