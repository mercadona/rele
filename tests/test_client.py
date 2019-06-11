import pytest
import concurrent
from unittest.mock import ANY, patch

from . import settings


@pytest.mark.usefixtures('publisher')
class TestPublisher:
    @patch('time.time', return_value=1560244246.863829)
    def test_returns_future_when_published_called(self, _time, publisher):
        message = {'foo': 'bar'}
        result = publisher.publish(topic='order-cancelled',
                                   data=message,
                                   myattr='hello')

        assert isinstance(result, concurrent.futures.Future)

        publisher._client.publish.assert_called_with(
            ANY,
            b'{"foo": "bar"}',
            myattr='hello',
            published_at='1560244246.863829')

    @patch('time.time', return_value=1560244246.863829)
    def test_save_log_when_published_called(self, _time, publisher, caplog):
        message = {'foo': 'bar'}

        publisher.publish(topic='order-cancelled',
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

    @patch('time.time', return_value=1560244246.863829)
    def test_publish_sets_published_at(self, _time, publisher):
        publisher.publish(topic='order-cancelled', data={'foo': 'bar'})

        publisher._client.publish.assert_called_with(
            ANY, b'{"foo": "bar"}', published_at='1560244246.863829')
