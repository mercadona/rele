import queue
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from google.cloud import pubsub_v1

from rele.config import Config
from rele.contrib.logging_middleware import LoggingMiddleware
from tests.subs import sub_stub


@pytest.fixture
def message_data():
    return {"foo": "bar"}


@pytest.fixture
def expected_message_data_log():
    return '{"foo": "bar"}'


@pytest.fixture
def expected_message_data_log_with_decimal():
    return '{"foo": "1"}'


@pytest.fixture
def message_wrapper(published_at, publish_time):
    rele_message = pubsub_v1.types.PubsubMessage(
        data='{"foo": "bar"}'.encode("utf-8"),
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
    return 'Message {\n  data: b\'{"foo": "bar"}\'\n  ordering_key: \'\'\n  attributes: {\n    "lang": "es",\n    "published_at": "1560244246.863829"\n  }\n}'


class TestLoggingMiddleware:
    @pytest.fixture
    def logging_middleware(self, config):
        logging_middleware = LoggingMiddleware()
        logging_middleware.setup(config)
        return logging_middleware

    @pytest.fixture
    def logging_middleware_with_custom_encoder(self, logging_middleware):
        config = Config(
            {
                "ENCODER_PATH": "django.core.serializers.json.DjangoJSONEncoder",
            }
        )
        logging_middleware.setup(config)
        return logging_middleware

    def test_message_payload_log_is_converted_to_string_on_post_publish_failure(
        self,
        logging_middleware,
        caplog,
        message_data,
        expected_message_data_log,
    ):
        logging_middleware.post_publish_failure(
            sub_stub, RuntimeError("💩"), message_data
        )

        message_log = caplog.records[0].subscription_message

        assert message_log == expected_message_data_log

    def test_message_payload_log_uses_custom_encoder(
        self,
        logging_middleware_with_custom_encoder,
        caplog,
        message_data,
        expected_message_data_log_with_decimal,
    ):
        message_data["foo"] = Decimal(1)

        logging_middleware_with_custom_encoder.post_publish_failure(
            sub_stub, RuntimeError("💩"), message_data
        )

        message_log = caplog.records[0].subscription_message

        assert message_log == expected_message_data_log_with_decimal

    def test_message_payload_log_is_converted_to_string_on_post_process_message_failure(
        self,
        logging_middleware,
        caplog,
        message_wrapper,
        expected_message_log,
    ):
        logging_middleware.post_process_message_failure(
            sub_stub, RuntimeError("💩"), 1, message_wrapper
        )

        message_log = caplog.records[0].subscription_message

        assert message_log == expected_message_log

    def test_post_publish_failure_message_payload_format_matches_post_process_message_failure_payload_type(
        self,
        logging_middleware,
        caplog,
        message_data,
        message_wrapper,
    ):
        logging_middleware.post_publish_failure(
            sub_stub, RuntimeError("💩"), message_data
        )
        logging_middleware.post_process_message_failure(
            sub_stub, RuntimeError("💩"), 1, message_wrapper
        )

        post_publish_failure_message_log = caplog.records[0].subscription_message
        post_process_message_message_log = caplog.records[1].subscription_message

        assert type(post_publish_failure_message_log) == type(
            post_process_message_message_log
        )
