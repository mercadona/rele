import pytest
import concurrent
from unittest.mock import MagicMock
from google.cloud.pubsub_v1 import PublisherClient
from rele import Publisher
from tests import settings


@pytest.fixture(scope='class')
def publisher():
    publisher = Publisher(settings.RELE_GC_PROJECT_ID,
                          settings.RELE_GC_CREDENTIALS)
    publisher._client = MagicMock(spec=PublisherClient)
    publisher._client.publish.return_value = concurrent.futures.Future()

    return publisher
