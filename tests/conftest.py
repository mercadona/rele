import pytest
import concurrent
from unittest.mock import MagicMock, patch
from google.cloud.pubsub_v1 import PublisherClient

from rele.config import Config
from rele import Publisher
from rele.client import Subscriber
from rele.middleware import register_middleware


@pytest.fixture
def project_id():
    return "test-project-id"


@pytest.fixture
def credentials():
    return "my-credentials"


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
    return Subscriber(project_id, credentials)


@pytest.fixture
def publisher(config):
    publisher = Publisher(config.gc_project_id, config.credentials)
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
