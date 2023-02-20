from datetime import datetime
import queue
from unittest.mock import MagicMock

import pytest
from google.cloud import pubsub_v1
from rele.config import Config

from rele.contrib.logging_middleware import LoggingMiddleware
from rele.contrib.verbose_logging_middleware import VerboseLoggingMiddleware
from tests.subs import sub_stub


@pytest.fixture
def long_message_wrapper(published_at, publish_time):
    long_string = "A" * 100
    rele_message = pubsub_v1.types.PubsubMessage(
        data=long_string.encode("utf-8"),
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
def message_wrapper(published_at, publish_time):
    rele_message = pubsub_v1.types.PubsubMessage(
        data="ABCDE".encode("utf-8"),
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
def expected_message_log():
    return 'Message {\n  data: b\'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\'\n  ordering_key: \'\'\n  attributes: {\n    "lang": "es",\n    "published_at": "1560244246.863829"\n  }\n}'


class TestVerboseLoggingMiddleware:
    @pytest.fixture
    def config(project_id):
        return Config(
            {
                "APP_NAME": "rele",
                "SUB_PREFIX": "rele",
                "GC_CREDENTIALS_PATH": "tests/dummy-pub-sub-credentials.json",
                "ENCODER_PATH": "rest_framework.utils.encoders.JSONEncoder",
                "MIDDLEWARE": ["rele.contrib.LoggingMiddleware"],
            }
        )

    @pytest.fixture
    def verbose_logging_middleware(self, config):
        verbose_logging_middleware = VerboseLoggingMiddleware()
        verbose_logging_middleware.setup(config)
        return verbose_logging_middleware

    @pytest.fixture
    def logging_middleware(self, config):
        logging_middleware = LoggingMiddleware()
        logging_middleware.setup(config)
        return logging_middleware

    def test_message_payload_log_is_not_truncated_on_post_process_failure(
        self,
        verbose_logging_middleware,
        caplog,
        long_message_wrapper,
        expected_message_log,
    ):
        verbose_logging_middleware.post_process_message_failure(
            sub_stub, RuntimeError("💩"), 1, long_message_wrapper
        )

        message_log = caplog.records[0].subscription_message

        assert message_log == expected_message_log

    def test_logs_message_data_when_message_is_successfully_published(self, verbose_logging_middleware, caplog):
        message_data = {
            "id": 123,
            "key": "confirmed",
            "timestamp": datetime.fromisoformat("2023-02-16T20:00:00+01:00"),
        }
        message_attributes = {"published_at": 1.0}

        verbose_logging_middleware.post_publish_success("pubsub-topic", message_data, message_attributes)

        emitted_log = caplog.records[0]
        assert emitted_log.message == "Successfully published to pubsub-topic"
        assert emitted_log.pubsub_publisher_attrs == {"published_at": 1.0}
        assert emitted_log.metrics == {
            "name": "publications",
            "data": {"agent": "rele", "topic": "pubsub-topic"},
        }
        assert emitted_log.subscription_message == (
            '{"id": 123, "key": "confirmed", "timestamp": "2023-02-16T20:00:00+01:00"}'
        )

    def test_logs_message_data_when_message_is_successfully_processed(
        self, verbose_logging_middleware, long_message_wrapper, expected_message_log, caplog
    ):
        verbose_logging_middleware.post_process_message_success(sub_stub, None, long_message_wrapper)

        emitted_log = caplog.records[-1]
        assert emitted_log.message == "Successfully processed message for rele-some-cool-topic - sub_stub"
        assert emitted_log.metrics == {
            "name": "subscriptions",
            "data": {
                "agent": "rele",
                "topic": "some-cool-topic",
                "status": "succeeded",
                "subscription": "rele-some-cool-topic",
                "attributes": {"lang": "es", "published_at": "1560244246.863829"},
            },
        }
        assert emitted_log.subscription_message == expected_message_log

    def test_post_process_failure_message_payload_format_matches_logging_middleware_format(
        self, verbose_logging_middleware, logging_middleware, caplog, message_wrapper
    ):
        verbose_logging_middleware.post_process_message_failure(
            sub_stub, RuntimeError("💩"), 1, message_wrapper
        )
        logging_middleware.post_process_message_failure(
            sub_stub, RuntimeError("💩"), 1, message_wrapper
        )

        verbose_message_log = caplog.records[0].subscription_message
        message_log = caplog.records[1].subscription_message

        assert verbose_message_log == message_log
