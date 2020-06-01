from unittest.mock import MagicMock, patch

import pytest

from rele import Publisher, publishing


class TestPublish:
    def test_raises_when_global_publisher_does_not_exist(self):
        message = {"foo": "bar"}

        with pytest.raises(ValueError):
            publishing.publish(topic="order-cancelled", data=message, myattr="hello")


class TestInitGlobalPublisher:
    @patch("rele.publishing.Publisher", autospec=True)
    def test_creates_global_publisher_when_published_called(
        self, mock_publisher, config
    ):
        mock_publisher.return_value = MagicMock(spec=Publisher)
        publishing.init_global_publisher(config)
        message = {"foo": "bar"}
        publishing.publish(topic="order-cancelled", data=message, myattr="hello")
        assert isinstance(publishing._publisher, Publisher)
        publisher_id = id(publishing._publisher)

        mock_publisher.return_value.publish.assert_called_with(
            "order-cancelled", {"foo": "bar"}, myattr="hello"
        )

        mock_publisher.return_value = MagicMock(spec=Publisher)
        publishing.publish(topic="order-cancelled", data=message, myattr="hello")
        assert id(publishing._publisher) == publisher_id
