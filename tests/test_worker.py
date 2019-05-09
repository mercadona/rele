from unittest.mock import ANY, patch

import pytest

from rele import Subscriber, Worker, sub


@sub(topic='some-cool-topic')
def sub_stub(data, **kwargs):
    print(f'I am a task doing stuff.')


class TestWorker:

    @patch.object(Subscriber, 'subscribe')
    def test_start_subscribes_and_saves_futures_when_subscriptions_given(
            self, mock_subscribe):
        subscriptions = (sub_stub,)
        worker = Worker(subscriptions)
        worker.start()

        mock_subscribe.assert_called_once_with(
            subscription_name='rele-some-cool-topic',
            callback=ANY
        )

    @patch.object(Subscriber, 'create_subscription')
    def test_setup_creates_subscription_when_topic_given(
            self, mock_create_subscription):
        subscriptions = (sub_stub,)
        worker = Worker(subscriptions)
        worker.setup()

        topic = 'some-cool-topic'
        subscription = 'rele-some-cool-topic'
        mock_create_subscription.assert_called_once_with(subscription, topic)

    @patch('rele.worker.db.connections.close_all')
    def test_stop_closes_db_connections(self, mock_db_close_all):
        subscriptions = (sub_stub,)
        worker = Worker(subscriptions)

        with pytest.raises(SystemExit):
            worker.stop()

        mock_db_close_all.assert_called_once()
