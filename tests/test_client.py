from unittest.mock import ANY, MagicMock

from google.cloud.pubsub_v1 import PublisherClient

from rele import Publisher


class TestPublisher:

    def test_returns_true_when_published_called(self):
        message = {'foo': 'bar'}
        publisher = Publisher()
        publisher._client = MagicMock(spec=PublisherClient)

        result = publisher.publish(topic='order-cancelled',
                                   data=message,
                                   event_type='cancellation')

        assert result is True
        publisher._client.publish.assert_called_with(
            ANY, b'{"foo":"bar"}', event_type='cancellation')
