import queue
from unittest.mock import MagicMock

import pytest
from google.cloud import pubsub_v1

from rele import Subscription
from rele.config import Config
from rele.contrib.unrecoverable_middleware import (
    UnrecoverableException,
    UnrecoverableMiddleWare,
)
from rele.middleware import register_middleware
from rele.subscription import Callback
from tests.subs import sub_stub


@pytest.fixture
def message_wrapper(published_at, publish_time):
    rele_message = pubsub_v1.types.PubsubMessage(
        data=b'{"id": 1}',
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
    message.nack = MagicMock(autospec=True)
    return message


class TestUnrecoverableMiddleWare:
    @pytest.fixture
    def unrecoverable_middleware(self, config):
        unrecoverable_middleware = UnrecoverableMiddleWare()
        unrecoverable_middleware.setup(config)
        return unrecoverable_middleware

    def test_acks_message_when_error_is_unrecoverable(
        self, unrecoverable_middleware, message_wrapper
    ):
        unrecoverable_middleware.post_process_message_failure(
            sub_stub,
            UnrecoverableException("required_property is required."),
            1,
            message_wrapper,
        )

        message_wrapper.ack.assert_called_once_with()
        message_wrapper.nack.assert_not_called()

    def test_acks_message_when_error_subclasses_unrecoverable_exception(
        self, unrecoverable_middleware, message_wrapper
    ):
        class IncompatiblePayload(UnrecoverableException):
            pass

        unrecoverable_middleware.post_process_message_failure(
            sub_stub, IncompatiblePayload("💩"), 1, message_wrapper
        )

        message_wrapper.ack.assert_called_once_with()

    @pytest.mark.parametrize(
        "err",
        [
            RuntimeError("💩"),
            ValueError("💩"),
            Exception("💩"),
        ],
    )
    def test_does_not_ack_message_when_error_is_recoverable(
        self, unrecoverable_middleware, message_wrapper, err
    ):
        unrecoverable_middleware.post_process_message_failure(
            sub_stub, err, 1, message_wrapper
        )

        message_wrapper.ack.assert_not_called()
        message_wrapper.nack.assert_not_called()


class TestUnrecoverableMiddleWareInCallback:
    @pytest.fixture
    def config_with_unrecoverable_middleware(self):
        return Config(
            {
                "APP_NAME": "rele",
                "SUB_PREFIX": "rele",
                "GC_CREDENTIALS_PATH": "tests/dummy-pub-sub-credentials.json",
                "MIDDLEWARE": ["rele.contrib.UnrecoverableMiddleWare"],
            }
        )

    @pytest.fixture
    def registered_unrecoverable_middleware(
        self, config, config_with_unrecoverable_middleware
    ):
        register_middleware(config=config_with_unrecoverable_middleware)
        yield
        register_middleware(config=config)

    def test_acks_message_when_subscription_raises_unrecoverable_exception(
        self, registered_unrecoverable_middleware, message_wrapper
    ):
        def raise_unrecoverable(data, **kwargs):
            raise UnrecoverableException("required_property is required.")

        callback = Callback(Subscription(raise_unrecoverable, "photo-uploaded"))

        callback(message_wrapper)

        message_wrapper.ack.assert_called_once_with()

    def test_does_not_ack_message_when_subscription_raises_other_exception(
        self, registered_unrecoverable_middleware, message_wrapper
    ):
        def raise_recoverable(data, **kwargs):
            raise RuntimeError("💩")

        callback = Callback(Subscription(raise_recoverable, "photo-uploaded"))

        callback(message_wrapper)

        message_wrapper.ack.assert_not_called()
