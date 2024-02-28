from unittest.mock import ANY, MagicMock, Mock, patch

import pytest

from rele import Publisher, publishing
from rele.config import Config
from tests import settings


class TestPublish:
    @patch("rele.publishing.Publisher", autospec=True)
    def test_instantiates_publisher_and_publishes_when_does_not_exist(
        self, mock_publisher
    ):
        with patch("rele.publishing.discover") as mock_discover:
            mock_discover.sub_modules.return_value = settings, []

            message = {"foo": "bar"}
            publishing.publish(topic="order-cancelled", data=message, myattr="hello")

            mock_publisher.return_value.publish.assert_called_with(
                "order-cancelled", {"foo": "bar"}, myattr="hello"
            )

    def test_raises_error_when_publisher_does_not_exists_and_settings_not_found(self):
        publishing._publisher = None
        message = {"foo": "bar"}

        with pytest.raises(ValueError):
            publishing.publish(topic="order-cancelled", data=message, myattr="hello")


class TestInitGlobalPublisher:
    @patch("rele.publishing.Publisher", autospec=True)
    def test_creates_global_publisher_when_published_called(
        self, mock_publisher, config
    ):
        publishing._publisher = None
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

    @patch("rele.publishing.Publisher", autospec=True)
    def test_creates_publisher_with_api_endpoint_option(self, mock_publisher, config):
        publishing._publisher = None
        mock_publisher.return_value = MagicMock(spec=Publisher)
        publishing.init_global_publisher(config)

        message = {"foo": "bar"}
        publishing.publish(topic="order-cancelled", data=message, myattr="hello")

        mock_publisher.assert_called_with(
            gc_project_id="rele-test",
            credentials=ANY,
            encoder=ANY,
            timeout=3.0,
            blocking=False,
            client_options={"api_endpoint": "custom-api.interconnect.example.com"},
        )
