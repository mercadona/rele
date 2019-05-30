import concurrent
from unittest.mock import ANY, MagicMock

from google.cloud.pubsub_v1 import PublisherClient

from rele import Publisher


class TestPublisher:

    def test_returns_future_when_published_called(self, caplog):
        message = {'foo': 'bar'}
        publisher = Publisher()
        publisher._client = MagicMock(spec=PublisherClient)
        publisher._client.publish.return_value = concurrent.futures.Future()

        result = publisher.publish(topic='order-cancelled',
                                   data=message,
                                   myattr='hello')

        assert isinstance(result, concurrent.futures.Future)
        publisher._client.publish.assert_called_with(
            ANY, b'{"foo":"bar"}', myattr='hello')

        log = caplog.records[0]
        assert log.message == 'Publishing to order-cancelled'
        assert log.pubsub_publisher_attrs == {'myattr': 'hello'}
