from unittest.mock import patch

import pytest
from google.api_core import exceptions
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1 import PublisherClient, SubscriberClient
from google.protobuf import duration_pb2
from google.pubsub_v1 import MessageStoragePolicy

from rele import Subscriber
from rele.retry_policy import RetryPolicy
from rele.subscription import Subscription


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
            request={
                "name": f"projects/rele-test/topics/{project_id}-test-topic",
                "message_storage_policy": MessageStoragePolicy(
                    {"allowed_persistence_regions": ["some-region"]}
                ),
            }
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
            config_with_retry_policy.gc_storage_region,
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
