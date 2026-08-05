import concurrent
import decimal
import importlib.util
import logging
import os
from concurrent.futures import TimeoutError
from unittest.mock import ANY, MagicMock, patch

import pytest
from google.cloud.pubsub_v1 import PublisherClient

import rele.client
from rele import Publisher


def _load_client_module_with_env(env):
    """Import a private copy of ``rele.client`` under a patched environment.

    ``rele.client.USE_EMULATOR`` is evaluated once, at import time, so the
    emulator branches can only be reached by importing the module again with
    ``PUBSUB_EMULATOR_HOST`` set. The copy is never registered in
    ``sys.modules``, which leaves the real ``rele.client`` (and the classes
    every other test holds a reference to) untouched.
    """
    spec = importlib.util.spec_from_file_location(
        "rele_client_with_emulator", rele.client.__file__
    )
    module = importlib.util.module_from_spec(spec)
    with patch.dict(os.environ, env):
        spec.loader.exec_module(module)
    return module


@pytest.mark.usefixtures("publisher", "time_mock")
class TestPublisher:
    @patch("rele.client.pubsub_v1.PublisherClient", autospec=True)
    def test_initialises_with_correct_parameters(self, mock_publisher_client, config):
        Publisher(
            gc_project_id=config.gc_project_id,
            credentials=config.credentials,
            encoder=config.encoder,
            timeout=config.publisher_timeout,
            blocking=config.publisher_blocking,
            client_options=config.client_options,
        )

        mock_publisher_client.assert_called_with(
            credentials=ANY,
            client_options={"api_endpoint": "custom-api.interconnect.example.com"},
        )

    @patch("rele.client.pubsub_v1.PublisherClient", autospec=True)
    def test_initialises_with_configured_timeout(
        self, mock_publisher_client, config, mock_future
    ):
        # Deliberately not the 3.0 default: asserting against
        # `config.publisher_timeout` would compare the default against itself and
        # would not notice the argument being dropped for a hardcoded 3.0.
        configured_timeout = 42.0

        publisher = Publisher(
            gc_project_id=config.gc_project_id,
            credentials=config.credentials,
            encoder=config.encoder,
            timeout=configured_timeout,
            blocking=True,
            client_options=config.client_options,
        )
        publisher._client = MagicMock(spec=PublisherClient)
        publisher._client.publish.return_value = mock_future

        publisher.publish(topic="order-cancelled", data={"foo": "bar"})

        mock_future.result.assert_called_once_with(timeout=configured_timeout)
        assert publisher._timeout == configured_timeout

    @patch("rele.client.pubsub_v1.PublisherClient", autospec=True)
    def test_initialises_without_credentials_when_emulator_host_is_set(
        self, mock_publisher_client, config
    ):
        client_module = _load_client_module_with_env(
            {"PUBSUB_EMULATOR_HOST": "localhost:8085"}
        )
        assert client_module.USE_EMULATOR is True

        client_module.Publisher(
            gc_project_id=config.gc_project_id,
            credentials=config.credentials,
            encoder=config.encoder,
            timeout=config.publisher_timeout,
            blocking=config.publisher_blocking,
            client_options=config.client_options,
        )

        mock_publisher_client.assert_called_once_with()

    def test_returns_future_when_published_called(self, published_at, publisher):
        message = {"foo": "bar"}
        result = publisher.publish(
            topic="order-cancelled", data=message, myattr="hello"
        )

        assert isinstance(result, concurrent.futures.Future)

        publisher._client.publish.assert_called_with(
            ANY,
            b'{"foo": "bar"}',
            myattr="hello",
            published_at=str(published_at),
        )

    def test_save_log_when_published_called(self, published_at, publisher, caplog):
        caplog.set_level(logging.DEBUG)
        message = {"foo": "bar"}
        publisher.publish(topic="order-cancelled", data=message, myattr="hello")

        log = caplog.records[0]

        assert log.message == "Publishing to order-cancelled"
        assert log.pubsub_publisher_attrs == {
            "myattr": "hello",
            "published_at": str(published_at),
        }
        assert log.metrics == {
            "name": "publications",
            "data": {"agent": "rele", "topic": "order-cancelled"},
        }

    def test_publish_sets_published_at(self, published_at, publisher):
        publisher.publish(topic="order-cancelled", data={"foo": "bar"})

        publisher._client.publish.assert_called_with(
            ANY, b'{"foo": "bar"}', published_at=str(published_at)
        )

    def test_publishes_to_a_topic_path_built_from_the_project_id(
        self, published_at, project_id, publisher
    ):
        publisher._client.topic_path.side_effect = PublisherClient.topic_path

        publisher.publish(topic="order-cancelled", data={"foo": "bar"})

        publisher._client.topic_path.assert_called_once_with(
            project_id, "order-cancelled"
        )
        publisher._client.publish.assert_called_once_with(
            f"projects/{project_id}/topics/order-cancelled",
            b'{"foo": "bar"}',
            published_at=str(published_at),
        )

    def test_publishes_data_with_custom_encoder(self, publisher, custom_encoder):
        publisher._encoder = custom_encoder
        publisher.publish(topic="order-cancelled", data=decimal.Decimal("1.20"))

        publisher._client.publish.assert_called_with(ANY, b"1.2", published_at=ANY)

    def test_publishes_data_with_client_timeout_when_blocking(
        self, mock_future, publisher
    ):
        publisher._timeout = 100.0
        publisher.publish(topic="order-cancelled", data={"foo": "bar"}, blocking=True)

        publisher._client.publish.return_value = mock_future
        publisher._client.publish.assert_called_with(
            ANY, b'{"foo": "bar"}', published_at=ANY
        )
        mock_future.result.assert_called_once_with(timeout=100)

    def test_publishes_data_with_client_timeout_when_blocking_by_default(
        self, mock_future, publisher
    ):
        publisher._timeout = 100.0
        publisher._blocking = True
        publisher.publish(topic="order-cancelled", data={"foo": "bar"})

        publisher._client.publish.return_value = mock_future
        publisher._client.publish.assert_called_with(
            ANY, b'{"foo": "bar"}', published_at=ANY
        )
        mock_future.result.assert_called_once_with(timeout=100)

    def test_publishes_data_non_blocking_by_default(self, mock_future, publisher):
        publisher._timeout = 100.0
        publisher.publish(topic="order-cancelled", data={"foo": "bar"})

        publisher._client.publish.return_value = mock_future
        publisher._client.publish.assert_called_with(
            ANY, b'{"foo": "bar"}', published_at=ANY
        )
        mock_future.result.assert_not_called()

    def test_publishes_data_with_client_timeout_when_blocking_and_timeout_specified(
        self, mock_future, publisher
    ):
        publisher._timeout = 100.0
        publisher.publish(
            topic="order-cancelled",
            data={"foo": "bar"},
            blocking=True,
            timeout=50,
        )

        publisher._client.publish.return_value = mock_future
        publisher._client.publish.assert_called_with(
            ANY, b'{"foo": "bar"}', published_at=ANY
        )
        mock_future.result.assert_called_once_with(timeout=50)

    def test_runs_post_publish_failure_hook_when_future_result_raises_timeout(
        self, mock_future, publisher, mock_post_publish_failure
    ):
        message = {"foo": "bar"}
        exception = TimeoutError()
        mock_future.result.side_effect = exception

        with pytest.raises(TimeoutError):
            publisher.publish(
                topic="order-cancelled", data=message, myattr="hello", blocking=True
            )
        mock_post_publish_failure.assert_called_once_with(
            "order-cancelled", exception, {"foo": "bar"}
        )

    def test_raises_when_timeout_error_and_raise_exception_is_true(
        self, publisher, mock_future
    ):
        message = {"foo": "bar"}
        e = TimeoutError()
        mock_future.result.side_effect = e

        with pytest.raises(TimeoutError):
            publisher.publish(
                topic="order-cancelled",
                data=message,
                myattr="hello",
                blocking=True,
                raise_exception=True,
            )

    def test_returns_future_when_timeout_error_and_raise_exception_is_false(
        self, publisher, mock_future
    ):
        message = {"foo": "bar"}
        e = TimeoutError()
        mock_future.result.side_effect = e

        result = publisher.publish(
            topic="order-cancelled",
            data=message,
            myattr="hello",
            blocking=True,
            raise_exception=False,
        )

        assert result is mock_future
