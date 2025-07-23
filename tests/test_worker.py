import time
from concurrent import futures
from concurrent.futures._base import FINISHED
from unittest.mock import ANY, create_autospec, patch

import pytest
from freezegun import freeze_time
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber.futures import StreamingPullFuture
from google.cloud.pubsub_v1.subscriber.scheduler import ThreadScheduler

from rele import Subscriber, Worker, sub
from rele.middleware import register_middleware
from rele.retry_policy import RetryPolicy
from rele.subscription import Callback
from rele.worker import NotConnectionError, create_and_run


@sub(topic="some-cool-topic", prefix="rele")
def sub_stub(data, **kwargs):
    print("I am a task doing stuff.")


@pytest.fixture
def worker(config):
    subscriptions = (sub_stub,)
    return Worker(
        subscriptions,
        config.client_options,
        config.gc_project_id,
        config.credentials,
        config.gc_storage_region,
        default_ack_deadline=60,
        threads_per_subscription=10,
        default_retry_policy=config.retry_policy,
    )


@pytest.fixture
def worker_without_client_options(config):
    subscriptions = (sub_stub,)
    return Worker(
        subscriptions,
        None,
        config.gc_project_id,
        config.credentials,
        config.gc_storage_region,
        default_ack_deadline=60,
        threads_per_subscription=10,
        default_retry_policy=config.retry_policy,
    )


@pytest.fixture
def mock_consume(config):
    with patch.object(Subscriber, "consume") as m:
        client = pubsub_v1.SubscriberClient(credentials=config.credentials)
        m.return_value = client.subscribe("dummy-subscription", Callback(sub_stub))
        yield m


@pytest.fixture
def mock_create_subscription():
    with patch.object(Subscriber, "update_or_create_subscription") as m:
        yield m


@pytest.fixture(autouse=True)
def mock_internet_connection():
    with patch("rele.worker.check_internet_connection", autospec=True) as m:
        m.return_value = True
        yield m


class TestWorker:
    def test_start_subscribes_and_saves_futures_when_subscriptions_given(
        self, mock_consume, worker
    ):
        worker.start()

        mock_consume.assert_called_once_with(
            subscription_name="rele-some-cool-topic",
            callback=ANY,
            scheduler=ANY,
        )
        scheduler = mock_consume.call_args_list[0][1]["scheduler"]
        assert isinstance(scheduler, ThreadScheduler)
        assert isinstance(scheduler._executor, futures.ThreadPoolExecutor)

    @patch.object(Worker, "_wait_forever")
    def test_run_sets_up_and_creates_subscriptions_when_called(
        self, mock_wait_forever, mock_consume, mock_create_subscription, worker
    ):
        worker.run_forever()

        mock_create_subscription.assert_called_once_with(sub_stub)
        mock_consume.assert_called_once_with(
            subscription_name="rele-some-cool-topic",
            callback=ANY,
            scheduler=ANY,
        )
        scheduler = mock_consume.call_args_list[0][1]["scheduler"]
        assert isinstance(scheduler, ThreadScheduler)
        assert isinstance(scheduler._executor, futures.ThreadPoolExecutor)
        mock_wait_forever.assert_called_once()

    @patch.object(Worker, "_wait_forever")
    @pytest.mark.usefixtures("mock_consume", "mock_create_subscription")
    def test_wait_forevers_for_custom_time_period_when_called_with_argument(
        self, mock_wait_forever, worker
    ):
        worker.run_forever(sleep_interval=127)

        mock_wait_forever.assert_called_once()

    @patch.object(Worker, "_wait_forever")
    def test_stop_cancels_futures_and_closes_subscriber(
        self, mock_wait_forever, mock_consume, mock_create_subscription, worker
    ):
        worker.run_forever()

        with pytest.raises(SystemExit):
            worker.stop()

        assert worker._futures[sub_stub]._state == FINISHED
        assert worker._subscriber._client._closed is True

    @patch("rele.contrib.django_db_middleware.db.connections.close_all")
    def test_stop_closes_db_connections(self, mock_db_close_all, config, worker):
        config.middleware = ["rele.contrib.DjangoDBMiddleware"]
        register_middleware(config=config)

        with pytest.raises(SystemExit):
            worker.stop()

        mock_db_close_all.assert_called_once()

    @pytest.mark.usefixtures("mock_create_subscription")
    def test_creates_subscription_with_custom_ack_deadline_from_environment(
        self, config
    ):
        subscriptions = (sub_stub,)
        custom_ack_deadline = 234
        worker = Worker(
            subscriptions,
            config.client_options,
            config.gc_project_id,
            config.credentials,
            config.gc_storage_region,
            custom_ack_deadline,
            threads_per_subscription=10,
        )
        worker.setup()

        assert worker._subscriber._ack_deadline == custom_ack_deadline
        assert worker._subscriber._gc_project_id == "rele-test"

    def test_raises_not_connection_error_during_start(
        self, worker_without_client_options, mock_internet_connection
    ):
        mock_internet_connection.return_value = False

        with pytest.raises(NotConnectionError):
            worker_without_client_options.start()
        mock_internet_connection.assert_called_once_with("www.google.com")

    def test_check_internet_connection_with_default_endpoint_if_client_options_do_not_have_api_endpoint(
        self, config, mock_internet_connection
    ):
        mock_internet_connection.return_value = False
        subscriptions = (sub_stub,)
        worker = Worker(
            subscriptions,
            {},
            config.gc_project_id,
            config.credentials,
            config.gc_storage_region,
            default_ack_deadline=60,
            threads_per_subscription=10,
            default_retry_policy=config.retry_policy,
        )

        with pytest.raises(NotConnectionError):
            worker.start()
        mock_internet_connection.assert_called_once_with("www.google.com")

    def test_check_internet_connection_uses_api_endpoint_setting_when_present(
        self, worker, mock_internet_connection
    ):
        mock_internet_connection.return_value = False

        with pytest.raises(NotConnectionError):
            worker.start()
        mock_internet_connection.assert_called_once_with(
            "custom-api.interconnect.example.com"
        )


@pytest.mark.usefixtures("mock_create_subscription")
class TestRestartConsumer:
    @pytest.fixture(autouse=True)
    def mock_sleep(self):
        with patch.object(time, "sleep", side_effect=ValueError) as m:
            yield m

    def test_does_not_restart_consumption_when_everything_goes_well(
        self, worker, mock_consume
    ):
        with pytest.raises(ValueError):
            worker.run_forever()

        assert len(mock_consume.call_args_list) == 1

    def test_restarts_consumption_when_future_is_cancelled(self, worker, mock_consume):
        mock_consume.return_value.cancel()

        with pytest.raises(ValueError):
            worker.run_forever()

        assert len(mock_consume.call_args_list) == 2

    def test_raises_future_error_when_future_with_exception_is_cancelled(
        self, worker, mock_create_subscription
    ):
        with patch.object(Subscriber, "consume") as m:
            mock_streaming_pull_future = create_autospec(
                spec=StreamingPullFuture, instance=True
            )
            mock_streaming_pull_future.cancelled.return_value = True
            mock_streaming_pull_future._state = FINISHED
            m.return_value = mock_streaming_pull_future

            with pytest.raises(ValueError):
                worker.run_forever()

        mock_streaming_pull_future.result.assert_called_once()

    def test_restarts_consumption_when_future_is_done(
        self, worker, mock_consume, mock_sleep
    ):
        mock_consume.return_value.set_result(True)

        with pytest.raises(ValueError):
            worker.run_forever()

        assert len(mock_consume.call_args_list) == 2

    @freeze_time("2024-01-01 10:00:50Z")
    @pytest.mark.usefixtures("mock_consume")
    def test_wait_forever_if_we_have_connection_and_timestamp_module_50(
        self, worker, mock_internet_connection
    ):
        with pytest.raises(ValueError):
            worker._wait_forever(1)

        mock_internet_connection.assert_called_once()

    @pytest.mark.usefixtures("mock_consume")
    @pytest.mark.parametrize(
        "timestamp_now", ["2024-01-01 10:00:49Z", "2024-01-01 10:00:51Z"]
    )
    def test_does_not_check_internet_connection_when_timestamp_is_not_module_50(
        self, worker, mock_internet_connection, timestamp_now
    ):
        with freeze_time(timestamp_now):
            with pytest.raises(ValueError):
                worker._wait_forever(1)

        mock_internet_connection.assert_not_called()

    @freeze_time("2024-01-01 10:00:50Z")
    def test_raises_not_connection_error_during_wait_forever_if_connection_is_down_every_50_seconds(  # noqa
        self, worker, mock_internet_connection
    ):
        mock_internet_connection.return_value = False

        with pytest.raises(NotConnectionError):
            worker._wait_forever(1)


class TestCreateAndRun:
    @pytest.fixture(autouse=True)
    def worker_wait_forever(self):
        with patch.object(Worker, "_wait_forever", return_value=None) as p:
            yield p

    @pytest.fixture
    def mock_worker(self):
        with patch("rele.worker.Worker", autospec=True) as p:
            yield p

    @pytest.fixture
    def mock_subscriber(self):
        with patch("rele.worker.Subscriber", autospec=True) as p:
            yield p

    def test_waits_forever_when_called_with_config_and_subs(
        self, config_with_retry_policy, mock_worker
    ):
        subscriptions = (sub_stub,)
        create_and_run(subscriptions, config_with_retry_policy)

        mock_worker.assert_called_with(
            subscriptions,
            None,
            "rele-test",
            ANY,
            "some-region",
            60,
            2,
            RetryPolicy(5, 30),
        )
        mock_worker.return_value.run_forever.assert_called_once_with()

    def test_creates_subscriber_with_correct_arguments(self, mock_subscriber, config):
        subscriptions = (sub_stub,)
        create_and_run(subscriptions, config)

        mock_subscriber.assert_called_with(
            "rele-test",
            ANY,
            "some-region",
            {"api_endpoint": "custom-api.interconnect.example.com"},
            60,
            None,
        )
