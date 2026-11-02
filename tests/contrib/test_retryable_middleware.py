import queue
from unittest.mock import MagicMock

import pytest
from google.cloud import pubsub_v1

from rele import Subscription
from rele.config import Config
from rele.contrib.retryable_middleware import (
    RetryableException,
    RetryableMiddleWare,
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


class TestRetryableMiddleWare:
    @pytest.fixture
    def retryable_middleware(self, config):
        retryable_middleware = RetryableMiddleWare()
        retryable_middleware.setup(config)
        return retryable_middleware

    def test_nacks_message_when_error_is_retryable(
        self, retryable_middleware, message_wrapper
    ):
        retryable_middleware.post_process_message_failure(
            sub_stub,
            RetryableException("upstream is unavailable."),
            1,
            message_wrapper,
        )

        message_wrapper.nack.assert_called_once_with()
        message_wrapper.ack.assert_not_called()

    def test_nacks_message_when_error_subclasses_retryable_exception(
        self, retryable_middleware, message_wrapper
    ):
        class TemporarilyUnavailable(RetryableException):
            pass

        retryable_middleware.post_process_message_failure(
            sub_stub, TemporarilyUnavailable("💩"), 1, message_wrapper
        )

        message_wrapper.nack.assert_called_once_with()

    @pytest.mark.parametrize(
        "err",
        [
            RuntimeError("💩"),
            ValueError("💩"),
            Exception("💩"),
        ],
    )
    def test_does_not_nack_message_when_error_is_not_retryable(
        self, retryable_middleware, message_wrapper, err
    ):
        retryable_middleware.post_process_message_failure(
            sub_stub, err, 1, message_wrapper
        )

        message_wrapper.nack.assert_not_called()
        message_wrapper.ack.assert_not_called()


class TestRetryableMiddleWareInCallback:
    @pytest.fixture
    def config_with_retryable_middleware(self):
        return Config(
            {
                "APP_NAME": "rele",
                "SUB_PREFIX": "rele",
                "GC_CREDENTIALS_PATH": "tests/dummy-pub-sub-credentials.json",
                "MIDDLEWARE": ["rele.contrib.RetryableMiddleWare"],
            }
        )

    @pytest.fixture
    def registered_retryable_middleware(self, config, config_with_retryable_middleware):
        register_middleware(config=config_with_retryable_middleware)
        yield
        register_middleware(config=config)

    def test_nacks_message_when_subscription_raises_retryable_exception(
        self, registered_retryable_middleware, message_wrapper
    ):
        def raise_retryable(data, **kwargs):
            raise RetryableException("upstream is unavailable.")

        callback = Callback(Subscription(raise_retryable, "photo-uploaded"))

        callback(message_wrapper)

        message_wrapper.nack.assert_called_once_with()

    def test_does_not_nack_message_when_subscription_raises_other_exception(
        self, registered_retryable_middleware, message_wrapper
    ):
        def raise_other(data, **kwargs):
            raise RuntimeError("💩")

        callback = Callback(Subscription(raise_other, "photo-uploaded"))

        callback(message_wrapper)

        message_wrapper.nack.assert_not_called()

    def test_does_not_nack_message_when_middleware_is_not_installed(
        self, config, message_wrapper
    ):
        def raise_retryable(data, **kwargs):
            raise RetryableException("upstream is unavailable.")

        callback = Callback(Subscription(raise_retryable, "photo-uploaded"))

        callback(message_wrapper)

        message_wrapper.nack.assert_not_called()
