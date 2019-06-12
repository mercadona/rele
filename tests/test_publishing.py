from unittest.mock import MagicMock, patch

from rele import Publisher, publishing

from . import settings


class TestPublish:

    @patch('rele.publishing.Publisher', autospec=True)
    def test_creates_global_publisher_when_published_called(
            self, mock_publisher):
        mock_publisher.return_value = MagicMock(spec=Publisher)
        publishing.init_global_publisher(settings.RELE_GC_PROJECT_ID,
                                         settings.RELE_GC_CREDENTIALS)
        message = {'foo': 'bar'}
        publishing.publish(
            topic='order-cancelled', data=message, myattr='hello')
        assert isinstance(publishing._publisher, Publisher)
        publisher_id = id(publishing._publisher)

        mock_publisher.return_value.publish.assert_called_with(
            'order-cancelled', {"foo": "bar"}, myattr='hello')

        mock_publisher.return_value = MagicMock(spec=Publisher)
        publishing.publish(
            topic='order-cancelled', data=message, myattr='hello')
        assert id(publishing._publisher) == publisher_id
