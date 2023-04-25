import concurrent
import decimal
import logging
from concurrent.futures import TimeoutError
from unittest.mock import ANY, patch

import pytest
from google.api_core import exceptions
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1 import PublisherClient, SubscriberClient
from google.protobuf import duration_pb2

from rele import Subscriber
from rele.retry_policy import RetryPolicy
from rele.subscription import Subscription


@pytest.mark.usefixtures("publisher", "time_mock")
class TestPublisher:
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


class TestSubscriber:
    @pytest.fixture(autouse=True)
    def mock_create_topic(self):
        with patch.object(
            PublisherClient, "create_topic", return_values={"name": "test-topic"}
        ) as mock:
            yield mock

    @patch.object(SubscriberClient, "create_subscription")
    def test_creates_subscription_with_default_ack_deadline_when_none_provided(
        self,
        _mocked_client,
        project_id,
        subscriber,
    ):
        expected_subscription = (
            f"projects/{project_id}/subscriptions/" f"{project_id}-test-topic"
        )
        expected_topic = f"projects/{project_id}/topics/" f"{project_id}-test-topic"

        subscriber.create_subscription(
            Subscription(None, topic=f"{project_id}-test-topic")
        )
        _mocked_client.assert_called_once_with(
            request={
                "ack_deadline_seconds": 60,
                "name": expected_subscription,
                "topic": expected_topic,
            }
        )
        assert subscriber._gc_project_id == "rele-test"

    @patch.object(SubscriberClient, "create_subscription")
    def test_creates_subscription_with_custom_ack_deadline_when_provided(
        self, _mocked_client, project_id, subscriber
    ):
        expected_subscription = (
            f"projects/{project_id}/subscriptions/" f"{project_id}-test-topic"
        )
        expected_topic = f"projects/{project_id}/topics/" f"{project_id}-test-topic"
        subscriber._ack_deadline = 100
        subscriber.create_subscription(
            Subscription(None, topic=f"{project_id}-test-topic")
        )

        _mocked_client.assert_called_once_with(
            request={
                "ack_deadline_seconds": 100,
                "name": expected_subscription,
                "topic": expected_topic,
            }
        )

    @patch.object(SubscriberClient, "create_subscription")
    def test_creates_subscription_with_backend_filter_by_when_provided(
        self, _mocked_client, project_id, subscriber
    ):
        expected_subscription = (
            f"projects/{project_id}/subscriptions/" f"{project_id}-test-topic"
        )
        expected_topic = f"projects/{project_id}/topics/" f"{project_id}-test-topic"
        backend_filter_by = "attributes:domain"
        subscriber.create_subscription(
            Subscription(
                None,
                topic=f"{project_id}-test-topic",
                backend_filter_by=backend_filter_by,
            )
        )

        _mocked_client.assert_called_once_with(
            request={
                "ack_deadline_seconds": 60,
                "name": expected_subscription,
                "topic": expected_topic,
                "filter": backend_filter_by,
            }
        )

    @patch.object(
        SubscriberClient,
        "create_subscription",
        side_effect=exceptions.AlreadyExists("Subscription already exists"),
    )
    def test_does_not_raise_when_subscription_already_exists(
        self, _mocked_client, project_id, subscriber
    ):
        subscriber.create_subscription(
            Subscription(None, topic=f"{project_id}-test-topic")
        )

        _mocked_client.assert_called()

    @patch.object(
        SubscriberClient,
        "create_subscription",
        side_effect=[exceptions.NotFound("Subscription topic does not exist"), True],
    )
    def test_creates_topic_when_subscription_topic_does_not_exist(
        self, _mocked_client, project_id, subscriber, mock_create_topic
    ):
        expected_subscription = (
            f"projects/{project_id}/subscriptions/" f"{project_id}-test-topic"
        )
        expected_topic = f"projects/{project_id}/topics/" f"{project_id}-test-topic"
        backend_filter_by = "attributes:domain"
        subscriber.create_subscription(
            Subscription(
                None,
                topic=f"{project_id}-test-topic",
                backend_filter_by=backend_filter_by,
            )
        )

        assert _mocked_client.call_count == 2
        mock_create_topic.assert_called_with(
            request={"name": f"projects/rele-test/topics/{project_id}-test-topic"}
        )

        _mocked_client.assert_called_with(
            request={
                "ack_deadline_seconds": 60,
                "name": expected_subscription,
                "topic": expected_topic,
                "filter": backend_filter_by,
            }
        )

    @patch.object(SubscriberClient, "create_subscription")
    def test_creates_subscription_with_retry_policy_when_provided(
        self, _mocked_client, project_id, subscriber
    ):
        expected_subscription = (
            f"projects/{project_id}/subscriptions/" f"{project_id}-test-topic"
        )
        expected_topic = f"projects/{project_id}/topics/" f"{project_id}-test-topic"
        expected_retry_policy = pubsub_v1.types.RetryPolicy(
            minimum_backoff=duration_pb2.Duration(seconds=10),
            maximum_backoff=duration_pb2.Duration(seconds=50),
        )

        subscriber.create_subscription(
            Subscription(
                None,
                topic=f"{project_id}-test-topic",
                retry_policy=RetryPolicy(10, 50),
            )
        )

        _mocked_client.assert_called_once_with(
            request={
                "ack_deadline_seconds": 60,
                "name": expected_subscription,
                "topic": expected_topic,
                "retry_policy": expected_retry_policy,
            }
        )

    @patch.object(SubscriberClient, "create_subscription")
    def test_default_retry_policy_is_applied_when_not_explicitly_provided(
        self, _mocked_client, project_id, config_with_retry_policy
    ):
        subscriber = Subscriber(
            config_with_retry_policy.gc_project_id,
            config_with_retry_policy.credentials,
            60,
            config_with_retry_policy.retry_policy,
        )
        expected_subscription = (
            f"projects/{project_id}/subscriptions/" f"{project_id}-test-topic"
        )
        expected_topic = f"projects/{project_id}/topics/" f"{project_id}-test-topic"
        expected_retry_policy = pubsub_v1.types.RetryPolicy(
            minimum_backoff=duration_pb2.Duration(seconds=5),
            maximum_backoff=duration_pb2.Duration(seconds=30),
        )

        subscriber.create_subscription(
            Subscription(
                None,
                topic=f"{project_id}-test-topic",
            )
        )

        _mocked_client.assert_called_once_with(
            request={
                "ack_deadline_seconds": 60,
                "name": expected_subscription,
                "topic": expected_topic,
                "retry_policy": expected_retry_policy,
            }
        )
