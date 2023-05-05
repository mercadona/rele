from unittest.mock import patch

import pytest
from google.api_core import exceptions
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1 import PublisherClient, SubscriberClient
from google.protobuf import duration_pb2
from google.cloud.pubsub_v1.types import FieldMask
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
    @patch.object(SubscriberClient, "update_subscription")
    def test_creates_subscription_with_default_ack_deadline_when_none_provided(
        self,
        client_update_subscription, client_create_subscription,
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
        client_create_subscription.assert_called_once_with(
            request={
                "ack_deadline_seconds": 60,
                "name": expected_subscription,
                "topic": expected_topic,
            }
        )
        assert subscriber._gc_project_id == "rele-test"

    @patch.object(SubscriberClient, "create_subscription")
    @patch.object(SubscriberClient, "update_subscription")
    def test_creates_subscription_with_custom_ack_deadline_when_provided(
        self, client_update_subscription, client_create_subscription, project_id, subscriber
    ):
        expected_subscription = (
            f"projects/{project_id}/subscriptions/" f"{project_id}-test-topic"
        )
        expected_topic = f"projects/{project_id}/topics/" f"{project_id}-test-topic"
        subscriber._ack_deadline = 100
        subscriber.create_subscription(
            Subscription(None, topic=f"{project_id}-test-topic")
        )

        client_create_subscription.assert_called_once_with(
            request={
                "ack_deadline_seconds": 100,
                "name": expected_subscription,
                "topic": expected_topic,
            }
        )

    @patch.object(SubscriberClient, "create_subscription")
    @patch.object(SubscriberClient, "update_subscription")
    def test_creates_subscription_with_backend_filter_by_when_provided(
        self, client_update_subscription, client_create_subscription, project_id, subscriber
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

        client_create_subscription.assert_called_once_with(
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
        side_effect=[exceptions.NotFound("Subscription topic does not exist"), True],
    )
    @patch.object(SubscriberClient, "update_subscription")
    def test_creates_topic_when_subscription_topic_does_not_exist(
        self, client_update_subscription, client_create_subscription, project_id, subscriber, mock_create_topic
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

        mock_create_topic.assert_called_with(
            request={
                "name": f"projects/rele-test/topics/{project_id}-test-topic",
                "message_storage_policy": MessageStoragePolicy(
                    {"allowed_persistence_regions": ["some-region"]}
                ),
            }
        )

        client_create_subscription.assert_called_with(
            request={
                "ack_deadline_seconds": 60,
                "name": expected_subscription,
                "topic": expected_topic,
                "filter": backend_filter_by,
            }
        )

    @patch.object(SubscriberClient, "create_subscription")
    @patch.object(SubscriberClient, "update_subscription")
    def test_creates_subscription_with_retry_policy_when_provided(
        self, client_update_subscription, client_create_subscription, project_id, subscriber
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

        client_create_subscription.assert_called_once_with(
            request={
                "ack_deadline_seconds": 60,
                "name": expected_subscription,
                "topic": expected_topic,
                "retry_policy": expected_retry_policy,
            }
        )

    @patch.object(SubscriberClient, "create_subscription")
    @patch.object(SubscriberClient, "update_subscription")
    def test_default_retry_policy_is_applied_when_not_explicitly_provided(
        self, client_update_subscription, client_create_subscription, project_id, config_with_retry_policy
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

        client_create_subscription.assert_called_once_with(
            request={
                "ack_deadline_seconds": 60,
                "name": expected_subscription,
                "topic": expected_topic,
                "retry_policy": expected_retry_policy,
            }
        )

    @patch.object(SubscriberClient, "create_subscription", side_effect=exceptions.AlreadyExists("Subscription already exists"))
    @patch.object(SubscriberClient, "update_subscription")
    def test_subscription_is_updated_with_retry_policy_when_already_exists(
        self, client_update_subscription, client_create_subscription, project_id, subscriber
    ):
        subscription_path = (
            f"projects/{project_id}/subscriptions/" f"{project_id}-test-topic"
        )
        topic_path = f"projects/{project_id}/topics/" f"{project_id}-test-topic"
        retry_policy = pubsub_v1.types.RetryPolicy(
            minimum_backoff=duration_pb2.Duration(seconds=10),
            maximum_backoff=duration_pb2.Duration(seconds=50),
        )

        subscription = pubsub_v1.types.Subscription(
            name=subscription_path,
            topic=topic_path,
            retry_policy=retry_policy,
        )

        update_mask = FieldMask(paths=["retry_policy"])

        subscriber.create_subscription(
            Subscription(
                None,
                topic=f"{project_id}-test-topic",
                retry_policy=RetryPolicy(10, 50),
            )
        )
        client_update_subscription.assert_called_once_with(
            request={
                "subscription": subscription, "update_mask": update_mask
            }
        )
