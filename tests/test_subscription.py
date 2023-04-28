import logging
import queue
import time
from unittest.mock import MagicMock, patch

import pytest
from google.cloud import pubsub_v1
from google.protobuf import timestamp_pb2

from rele import Callback, Subscription, sub
from rele.middleware import register_middleware
from rele.retry_policy import RetryPolicy

logger = logging.getLogger(__name__)


@sub(topic="some-cool-topic", prefix="rele")
def sub_stub(data, **kwargs):
    logger.info(f'I am a task doing stuff with ID {data["id"]} ' f'({kwargs["lang"]})')
    return data["id"]


@sub(topic="some-fancy-topic")
def sub_fancy_stub(data, **kwargs):
    logger.info(
        f'I used to have a prefix, but not anymore, only {data["id"]}'
        f'id {kwargs["lang"]}'
    )
    return data["id"]


@sub(topic="published-time-type")
def sub_published_time_type(data, **kwargs):
    logger.info(f'{type(kwargs["published_at"])}')


def landscape_filter(kwargs):
    return kwargs.get("type") == "landscape"


def gif_filter(kwargs):
    return kwargs.get("format") == "gif"


@sub(topic="photo-updated", filter_by=landscape_filter)
def sub_process_landscape_photos(data, **kwargs):
    return f'Received a photo of type {kwargs.get("type")}'


@sub(topic="photo-updated", filter_by=[landscape_filter, gif_filter])
def sub_process_landscape_gif_photos(data, **kwargs):
    return f'Received a {kwargs.get("format")} photo of type {kwargs.get("type")}'


class TestSubscription:
    def test_subs_return_subscription_objects(self):
        assert isinstance(sub_stub, Subscription)
        assert sub_stub.topic == "some-cool-topic"
        assert sub_stub.name == "rele-some-cool-topic"

    def test_subs_without_prefix_return_subscription_objects(self):
        assert isinstance(sub_fancy_stub, Subscription)
        assert sub_fancy_stub.topic == "some-fancy-topic"
        assert sub_fancy_stub.name == "some-fancy-topic"

    def test_executes_callback_when_called(self, caplog):
        res = sub_stub({"id": 123}, **{"lang": "es"})

        assert res == 123
        log2 = caplog.records[0]
        assert log2.message == "I am a task doing stuff with ID 123 (es)"

    def test_sub_executes_when_message_attributes_match_criteria(self):
        data = {"name": "my_new_photo.jpeg"}
        response = sub_process_landscape_photos(data, type="landscape")

        assert response == "Received a photo of type landscape"

    def test_sub_does_not_execute_when_message_attributes_dont_match_criteria(
        self,
    ):
        data = {"name": "my_new_photo.jpeg"}
        response = sub_process_landscape_photos(data, type="")

        assert response is None

    def test_sub_executes_when_message_attributes_matches_multiple_criterias(
        self,
    ):
        data = {"name": "my_new_photo.jpeg"}
        response = sub_process_landscape_gif_photos(
            data, type="landscape", format="gif"
        )

        assert response == "Received a gif photo of type landscape"

    @pytest.mark.parametrize(
        "type, format",
        [
            ("portrait", "gif"),
            ("landscape", "jpg"),
            ("portrait", "jpg"),
            (None, "gif"),
            ("portrait", None),
            (None, None),
        ],
    )
    def test_sub_is_not_executed_when_message_attribs_dont_match_all_criterias(
        self, type, format
    ):
        data = {"name": "my_new_photo.jpeg"}
        response = sub_process_landscape_gif_photos(data, type=type, format=format)

        assert response is None

    def test_raises_error_when_filter_by_is_not_valid(self):
        Subscription(
            func=lambda x: None, topic="topic", prefix="rele", filter_by=lambda x: True
        )
        Subscription(
            func=lambda x: None,
            topic="topic",
            prefix="rele",
            filter_by=((lambda x: True),),
        )

        with pytest.raises(ValueError):
            Subscription(func=lambda x: None, topic="topic", prefix="rele", filter_by=1)

        with pytest.raises(ValueError):
            Subscription(
                func=lambda x: None, topic="topic", prefix="rele", filter_by=(1,)
            )


class TestCallback:
    @pytest.fixture(autouse=True)
    def mock_close_old_connections(self):
        with patch(
            "rele.contrib.django_db_middleware.db." "close_old_connections"
        ) as mock_old_connections:
            yield mock_old_connections

    @pytest.fixture
    def published_at(self):
        return time.time()

    @pytest.fixture
    def publish_time(self):
        timestamp = timestamp_pb2.Timestamp()
        timestamp.GetCurrentTime()
        return timestamp

    @pytest.fixture
    def message_wrapper(self, published_at, publish_time):
        rele_message = pubsub_v1.types.PubsubMessage(
            data=b'{"id": 123}',
            attributes={"lang": "es", "published_at": str(published_at)},
            message_id="1",
            publish_time=publish_time,
        )

        message = pubsub_v1.subscriber.message.Message(
            rele_message._pb,
            "ack-id",
            delivery_attempt=1,
            request_queue=queue.Queue(),
        )
        message.ack = MagicMock(autospec=True)
        return message

    @pytest.fixture
    def message_wrapper_empty(self):
        rele_message = pubsub_v1.types.PubsubMessage(
            data=b"", attributes={"lang": "es"}, message_id="1"
        )
        message = pubsub_v1.subscriber.message.Message(
            rele_message, "ack-id", MagicMock()
        )
        message.ack = MagicMock(autospec=True)
        return message

    @pytest.fixture
    def message_wrapper_invalid_json(self, publish_time):
        rele_message = pubsub_v1.types.PubsubMessage(
            data=b"foobar",
            attributes={},
            message_id="1",
            publish_time=publish_time,
        )
        message = pubsub_v1.subscriber.message.Message(
            rele_message._pb,
            "ack-id",
            delivery_attempt=1,
            request_queue=queue.Queue(),
        )
        message.ack = MagicMock(autospec=True)
        return message

    def test_log_start_processing_when_callback_called(
        self, caplog, message_wrapper, published_at
    ):
        with caplog.at_level(logging.DEBUG):
            callback = Callback(sub_stub)
            res = callback(message_wrapper)

        assert res == 123
        log1 = caplog.records[0]
        assert log1.message == (
            "Start processing message for " "rele-some-cool-topic - sub_stub"
        )
        assert log1.metrics == {
            "name": "subscriptions",
            "data": {
                "agent": "rele",
                "topic": "some-cool-topic",
                "status": "received",
                "subscription": "rele-some-cool-topic",
                "attributes": {
                    "lang": "es",
                    "published_at": str(published_at),
                },
            },
        }

    def test_acks_message_when_execution_successful(self, caplog, message_wrapper):
        with caplog.at_level(logging.DEBUG):
            callback = Callback(sub_stub)
            res = callback(message_wrapper)

        assert res == 123
        message_wrapper.ack.assert_called_once()
        assert len(caplog.records) == 3
        message_wrapper_log = caplog.records[1]
        assert message_wrapper_log.message == (
            "I am a task doing " "stuff with ID 123 (es)"
        )

    def test_log_when_execution_is_succesful(
        self, message_wrapper, caplog, published_at
    ):
        callback = Callback(sub_stub)
        callback(message_wrapper)

        success_log = caplog.records[-1]
        assert success_log.message == (
            "Successfully processed message for " "rele-some-cool-topic - sub_stub"
        )
        assert success_log.metrics == {
            "name": "subscriptions",
            "data": {
                "agent": "rele",
                "topic": "some-cool-topic",
                "status": "succeeded",
                "subscription": "rele-some-cool-topic",
                "duration_seconds": pytest.approx(0.5, abs=0.5),
                "attributes": {
                    "lang": "es",
                    "published_at": str(published_at),
                },
            },
        }

    def test_log_does_not_ack_called_message_when_execution_fails(
        self, caplog, message_wrapper, published_at
    ):
        @sub(topic="some-cool-topic", prefix="rele")
        def crashy_sub_stub(data, **kwargs):
            raise ValueError("I am an exception from a sub")

        callback = Callback(crashy_sub_stub)
        res = callback(message_wrapper)

        assert res is None
        message_wrapper.ack.assert_not_called()
        failed_log = caplog.records[-1]
        assert failed_log.message == (
            "Exception raised while processing "
            "message for rele-some-cool-topic - "
            "crashy_sub_stub: ValueError"
        )
        assert failed_log.metrics == {
            "name": "subscriptions",
            "data": {
                "agent": "rele",
                "topic": "some-cool-topic",
                "status": "failed",
                "subscription": "rele-some-cool-topic",
                "duration_seconds": pytest.approx(0.5, abs=0.5),
                "attributes": {
                    "lang": "es",
                    "published_at": str(published_at),
                },
            },
        }
        assert failed_log.subscription_message == str(message_wrapper)

    def test_log_acks_called_message_when_not_json_serializable(
        self, caplog, message_wrapper_invalid_json, published_at
    ):
        callback = Callback(sub_stub)
        res = callback(message_wrapper_invalid_json)

        assert res is None
        message_wrapper_invalid_json.ack.assert_called_once()
        failed_log = caplog.records[-1]
        assert failed_log.message == (
            "Exception raised while processing "
            "message for rele-some-cool-topic - "
            "sub_stub: JSONDecodeError"
        )
        assert failed_log.metrics == {
            "name": "subscriptions",
            "data": {
                "agent": "rele",
                "topic": "some-cool-topic",
                "status": "failed",
                "subscription": "rele-some-cool-topic",
                "duration_seconds": pytest.approx(0.5, abs=0.5),
                "attributes": {},
            },
        }
        assert failed_log.subscription_message == str(message_wrapper_invalid_json)

    def test_published_time_as_message_attribute(self, message_wrapper, caplog):
        callback = Callback(sub_published_time_type)
        callback(message_wrapper)

        success_log = caplog.records[-2]
        assert success_log.message == "<class 'float'>"

    def test_old_django_connections_closed_when_middleware_is_used(
        self, mock_close_old_connections, message_wrapper, config
    ):
        config.middleware = ["rele.contrib.DjangoDBMiddleware"]
        register_middleware(config)
        callback = Callback(sub_stub)
        res = callback(message_wrapper)

        assert res == 123
        assert mock_close_old_connections.call_count == 2


class TestDecorator:
    def test_returns_subscription_when_callback_valid(self):
        subscription = sub(topic="topic", prefix="rele")(lambda data, **kwargs: None)
        assert isinstance(subscription, Subscription)

    def test_raises_error_when_function_signature_is_not_valid(self):
        with pytest.raises(RuntimeError):
            sub(topic="topic", prefix="rele")(lambda: None)

        with pytest.raises(RuntimeError):
            sub(topic="topic", prefix="rele")(lambda data: None)

        with pytest.raises(RuntimeError):
            sub(topic="topic", prefix="rele")(lambda data, value=None: None)

    def test_logs_warning_when_function_not_in_subs_module(self, caplog):
        sub(topic="topic", prefix="rele")(lambda data, **kwargs: None)
        assert (
            "Subscription function tests.test_subscription.<lambda> is outside a subs "
            "module that will not be discovered." in caplog.text
        )

    def test_retry_policy_is_applied_when_specified(self):
        subscription = sub(
            topic="topic",
            prefix="rele",
            retry_policy=RetryPolicy(1, 10),
        )(lambda data, **kwargs: None)

        assert subscription.retry_policy == RetryPolicy(1, 10)
