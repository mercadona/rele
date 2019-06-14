from unittest.mock import ANY, patch

import pytest

from rele import Subscriber, Worker, sub
from rele.middleware import register_middleware


@sub(topic='some-cool-topic', prefix='rele')
def sub_stub(data, **kwargs):
    print(f'I am a task doing stuff.')


class TestWorker:

    @patch.object(Subscriber, 'consume')
    def test_start_subscribes_and_saves_futures_when_subscriptions_given(
            self, mock_consume, project_id, credentials):
        subscriptions = (sub_stub,)
        worker = Worker(subscriptions, project_id, credentials)
        worker.start()

        mock_consume.assert_called_once_with(
            subscription_name='rele-some-cool-topic',
            callback=ANY
        )

    @patch.object(Subscriber, 'create_subscription')
    def test_setup_creates_subscription_when_topic_given(
            self, mock_create_subscription, project_id, credentials):
        subscriptions = (sub_stub,)
        worker = Worker(subscriptions, project_id, credentials)
        worker.setup()

        topic = 'some-cool-topic'
        subscription = 'rele-some-cool-topic'
        mock_create_subscription.assert_called_once_with(subscription, topic)

    @patch('rele.contrib.django_db_middleware.db.connections.close_all')
    def test_stop_closes_db_connections(
            self, mock_db_close_all, config,  project_id, credentials):
        config.middleware = ['rele.contrib.DjangoDBMiddleware']
        register_middleware(config=config)
        subscriptions = (sub_stub,)
        worker = Worker(subscriptions, project_id, credentials)

        with pytest.raises(SystemExit):
            worker.stop()

        mock_db_close_all.assert_called_once()
