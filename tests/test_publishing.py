from unittest.mock import MagicMock, patch

from rele import Publisher, publishing


class TestPublish:

    @patch('rele.publishing.Publisher', autospec=True)
    def test_creates_global_publisher_when_published_called(
            self, mock_publisher, project_id, credentials):
        mock_publisher.return_value = MagicMock(spec=Publisher)
        publishing.init_global_publisher(project_id, credentials)
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
