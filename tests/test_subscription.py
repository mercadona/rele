import logging
from unittest import mock
from unittest.mock import MagicMock, patch, ANY

import pytest
from google.cloud import pubsub_v1

from rele import Callback, Subscription, sub

logger = logging.getLogger(__name__)


@sub(topic='some-cool-topic')
def sub_stub(data, **kwargs):
    logger.info(f'I am a task doing stuff with ID {data["id"]} '
                f'({kwargs["lang"]})')


class TestSubscription:

    def test_subs_return_subscription_objects(self):
        assert isinstance(sub_stub, Subscription)
        assert sub_stub.topic == 'some-cool-topic'
        assert sub_stub.name == 'rele-some-cool-topic'

    def test_executes_callback_when_called(self, caplog):
        res = sub_stub({'id': 123}, **{'lang': 'es'})

        assert res is None
        log2 = caplog.records[0]
        assert log2.message == 'I am a task doing stuff with ID 123 (es)'


class TestCallback:

    @pytest.fixture(autouse=True)
    def mock_close_old_connections(self):
        with patch('rele.subscription.db.'
                   'close_old_connections') as mock_old_connections:
            yield mock_old_connections

    @pytest.fixture
    def message_wrapper(self):
        rele_message = pubsub_v1.types.PubsubMessage(
            data=b'{"id": 123}', attributes={'lang': 'es'}, message_id='1')
        return pubsub_v1.subscriber.message.Message(
            rele_message, 'ack-id', MagicMock())

    def test_acks_message_when_callback_called(self, caplog, message_wrapper):
        with caplog.at_level(logging.DEBUG):
            callback = Callback(sub_stub)
            res = callback(message_wrapper)

        assert res is None
        log1 = caplog.records[0]
        assert log1.message == ('Start processing message for '
                                'rele-some-cool-topic - sub_stub')
        assert log1.metrics == {
            'name': 'subscriptions',
            'data': {
                'agent': 'rele',
                'topic': 'some-cool-topic',
                'status': 'received',
                'subscription': 'rele-some-cool-topic',
            }
        }
        log2 = caplog.records[1]
        assert log2.message == 'I am a task doing stuff with ID 123 (es)'

    def test_does_not_ack_message_when_callback_raises(
            self, caplog, message_wrapper):
        @sub(topic='some-cool-topic')
        def crashy_sub_stub(message, **kwargs):
            raise ValueError('I am an exception from a sub')

        callback = Callback(crashy_sub_stub)
        res = callback(message_wrapper)

        assert res is None
        failed_log = caplog.records[-1]
        assert failed_log.message == ('Exception raised while processing '
                                      'message for rele-some-cool-topic - '
                                      'crashy_sub_stub: ValueError')
        assert failed_log.metrics == {
            'name': 'subscriptions',
            'data': {
              'agent': 'rele',
                'topic': 'some-cool-topic',
                'status': 'failed',
                'subscription': 'rele-some-cool-topic',
                'duration_seconds': pytest.approx(0.0, 0.1)
            }
        }

    def test_log_when_callback_is_succesfull(self, message_wrapper, caplog):
        callback = Callback(sub_stub)
        res = callback(message_wrapper)

        success_log = caplog.records[1]
        assert success_log.message == ('Successfully processed message for '
                                'rele-some-cool-topic - sub_stub')
        assert success_log.metrics == {
            'name': 'subscriptions',
            'data': {
                'agent': 'rele',
                'topic': 'some-cool-topic',
                'status': 'success',
                'subscription': 'rele-some-cool-topic',
                'duration_seconds': pytest.approx(0.0, 0.1)
            }
        }
