import decimal
import concurrent
from unittest.mock import ANY, patch

import pytest
from google.cloud.pubsub_v1 import SubscriberClient


@pytest.mark.usefixtures("publisher", "time_mock")
class TestPublisher:
    def test_returns_future_when_published_called(self, published_at, publisher):
        message = {"foo": "bar"}
        result = publisher.publish(
            topic="order-cancelled", data=message, myattr="hello"
        )

        assert isinstance(result, concurrent.futures.Future)

        publisher._client.publish.assert_called_with(
            ANY, b'{"foo": "bar"}', myattr="hello", published_at=str(published_at)
        )

    def test_save_log_when_published_called(self, published_at, publisher, caplog):
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

    def test_publishes_data_with_custom_encoder(self, publisher, custom_encoder):
        publisher._encoder = custom_encoder
        publisher.publish(topic="order-cancelled", data=decimal.Decimal("1.20"))

        publisher._client.publish.assert_called_with(ANY, b"1.2", published_at=ANY)

    @patch.object(concurrent.futures.Future, "result")
    def test_publishes_data_with_client_timeout_when_blocking(
        self, mock_future, publisher
    ):
        publisher._timeout = 100.0
        publisher.publish(topic="order-cancelled", data={"foo": "bar"}, blocking=True)

        publisher._client.publish.return_value = mock_future
        publisher._client.publish.assert_called_with(
            ANY, b'{"foo": "bar"}', published_at=ANY
        )
        mock_future.assert_called_once_with(timeout=100)

    @patch.object(concurrent.futures.Future, "result")
    def test_publishes_data_with_method_timeout_when_blocking(
        self, mock_future, publisher
    ):
        publisher._timeout = 100.0
        publisher.publish(
            topic="order-cancelled", data={"foo": "bar"}, blocking=True, timeout=50.0
        )

        publisher._client.publish.return_value = mock_future
        publisher._client.publish.assert_called_with(
            ANY, b'{"foo": "bar"}', published_at=ANY
        )
        mock_future.assert_called_once_with(timeout=50.0)


class TestSubscriber:
    @patch.object(SubscriberClient, "create_subscription")
    def test_creates_subscription_with_default_ack_deadline_when_none_provided(
        self, _mocked_client, project_id, subscriber
    ):
        expected_subscription = f"projects/{project_id}/subscriptions/" f"test-topic"
        expected_topic = f"projects/{project_id}/topics/" f"{project_id}-test-topic"

        subscriber.create_subscription("test-topic", f"{project_id}-test-topic")

        _mocked_client.assert_called_once_with(
            ack_deadline_seconds=60, name=expected_subscription, topic=expected_topic
        )

    @patch.object(SubscriberClient, "create_subscription")
    def test_creates_subscription_with_custom_ack_deadline_when_provided(
        self, _mocked_client, project_id, subscriber
    ):
        expected_subscription = f"projects/{project_id}/subscriptions/" f"test-topic"
        expected_topic = f"projects/{project_id}/topics/" f"{project_id}-test-topic"
        subscriber._ack_deadline = 100
        subscriber.create_subscription(
            subscription="test-topic", topic=f"{project_id}-test-topic"
        )

        _mocked_client.assert_called_once_with(
            ack_deadline_seconds=100, name=expected_subscription, topic=expected_topic
        )
