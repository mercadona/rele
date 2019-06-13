import pytest
import concurrent
from unittest.mock import ANY


@pytest.mark.usefixtures('publisher', 'time_mock')
class TestPublisher:
    def test_returns_future_when_published_called(
            self, published_at, publisher):
        message = {'foo': 'bar'}
        result = publisher.publish(topic='order-cancelled',
                                   data=message,
                                   myattr='hello')

        assert isinstance(result, concurrent.futures.Future)

        publisher._client.publish.assert_called_with(
            ANY,
            b'{"foo": "bar"}',
            myattr='hello',
            published_at=str(published_at))

    def test_save_log_when_published_called(
            self, published_at, publisher, caplog):
        message = {'foo': 'bar'}

        publisher.publish(topic='order-cancelled',
                          data=message,
                          myattr='hello')

        log = caplog.records[0]

        assert log.message == 'Publishing to order-cancelled'
        assert log.pubsub_publisher_attrs == {
            'myattr': 'hello',
            'published_at': str(published_at)
        }
        assert log.metrics == {
            'name': 'publications',
            'data': {
                'agent': 'rele',
                'topic': 'order-cancelled',
            }
        }

    def test_publish_sets_published_at(self, published_at, publisher):
        publisher.publish(topic='order-cancelled', data={'foo': 'bar'})

        publisher._client.publish.assert_called_with(
            ANY, b'{"foo": "bar"}', published_at=str(published_at))
