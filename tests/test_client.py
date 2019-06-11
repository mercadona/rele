import concurrent
import time
from unittest.mock import ANY, MagicMock, patch

from google.cloud.pubsub_v1 import PublisherClient

from rele import Publisher

from . import settings


class TestPublisher:
    @classmethod
    def setup_method(cls):
        cls.publisher = Publisher()
        cls.publisher._client = MagicMock(spec=PublisherClient)
        cls.publisher._client.publish.return_value = concurrent.futures.Future()

    @patch('time.time', return_value=1560244246.863829)
    def test_returns_future_when_published_called(self, mocked_time):
        message = {'foo': 'bar'}
        result = self.publisher.publish(topic='order-cancelled',
                                   data=message,
                                   myattr='hello')

        assert isinstance(result, concurrent.futures.Future)

        self.publisher._client.publish.assert_called_with(ANY,
                                                          b'{"foo": "bar"}',
                                                          myattr='hello',
                                                          published_at='1560244246.863829')

    @patch('time.time', return_value=1560244246.863829)
    def test_save_log_when_published_called(self, mocked_time, caplog):
        message = {'foo': 'bar'}

        self.publisher.publish(topic='order-cancelled',
                               data=message,
                               myattr='hello')

        log = caplog.records[0]

        assert log.message == 'Publishing to order-cancelled'
        assert log.pubsub_publisher_attrs == {
            'myattr': 'hello',
            'published_at': '1560244246.863829'
        }
        assert log.metrics == {
            'name': 'publications',
            'data': {
                'agent': 'rele',
                'topic': 'order-cancelled',
            }
        }

    def test_set_published_at_as_argument(self):
        message = {'foo': 'bar'}
        expected_time = str(time.time())

        self.publisher.publish(topic='order-cancelled',
                               data=message,
                               published_at=expected_time)

        self.publisher._client.publish.assert_called_with(ANY,
                                                          b'{"foo": "bar"}',
                                                          published_at=expected_time)
