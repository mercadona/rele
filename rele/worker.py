import logging
import signal
import sys
import time
from concurrent import futures

from google.cloud.pubsub_v1.subscriber.scheduler import ThreadScheduler

from .client import Subscriber
from .middleware import run_middleware_hook
from .subscription import Callback

logger = logging.getLogger(__name__)


class Worker:
    """A Worker manages the subscriptions which consume Google PubSub messages.

    Facilitates the creation of subscriptions if not already created,
    and the starting and stopping the consumption of them.

    :param subscriptions: list :class:`~rele.subscription.Subscription`
    """

    def __init__(
        self,
        subscriptions,
        gc_project_id=None,
        credentials=None,
        default_ack_deadline=None,
        threads_per_subscription=None,
    ):
        self._subscriber = Subscriber(gc_project_id, credentials, default_ack_deadline)
        self._futures = {}
        self._subscriptions = subscriptions
        self.threads_per_subscription = threads_per_subscription

    def setup(self):
        """Create the subscriptions on a Google PubSub topic.

        If the subscription already exists, the subscription will not be
        re-created. Therefore, it is idempotent.
        """
        for subscription in self._subscriptions:
            self._subscriber.create_subscription(subscription)

    def start(self):
        """Begin consuming all subscriptions.

        When consuming a subscription, a ``StreamingPullFuture`` is returned from
        the Google PubSub client library. This future can be used to
        manage the background stream.

        The futures are stored so that they can be cancelled later on
        for a graceful shutdown of the worker.
        """
        run_middleware_hook("pre_worker_start")
        for subscription in self._subscriptions:
            self._boostrap_consumption(subscription)
        run_middleware_hook("post_worker_start")

    def run_forever(self, sleep_interval=1):
        """Shortcut for calling setup, start, and _wait_forever.

        :param sleep_interval: Number of seconds to sleep in the ``while True`` loop
        """
        self.setup()
        self.start()
        self._wait_forever(sleep_interval=sleep_interval)

    def stop(self, signal=None, frame=None):
        """Manage the shutdown process of the worker.

        This function has two purposes:

            1. Cancel all the futures created.
            2. And close all the database connections
               opened by Django. Even though we cancel the connections
               for every execution of the callback, we want to be sure
               that all the database connections are closed
               in this process.

        Exits with code 0 for a clean exit.

        :param signal: Needed for `signal.signal <https://docs.python.org/3/library/signal.html#signal.signal>`_  # noqa
        :param frame: Needed for `signal.signal <https://docs.python.org/3/library/signal.html#signal.signal>`_  # noqa
        """
        run_middleware_hook("pre_worker_stop", self._subscriptions)
        for future in self._futures.values():
            future.cancel()

        run_middleware_hook("post_worker_stop")
        sys.exit(0)

    def _boostrap_consumption(self, subscription):
        if subscription in self._futures:
            self._futures[subscription].cancel()

        executor_kwargs = {"thread_name_prefix": "ThreadPoolExecutor-ThreadScheduler"}
        executor = futures.ThreadPoolExecutor(
            max_workers=self.threads_per_subscription, **executor_kwargs
        )
        scheduler = ThreadScheduler(executor=executor)

        self._futures[subscription] = self._subscriber.consume(
            subscription_name=subscription.name,
            callback=Callback(subscription),
            scheduler=scheduler,
        )

    def _wait_forever(self, sleep_interval):
        logger.info("Consuming subscriptions...")
        while True:
            for subscription, future in self._futures.items():
                if future.cancelled() or future.done():
                    logger.info(f"Restarting consumption of {subscription.name}.")
                    self._boostrap_consumption(subscription)

            time.sleep(sleep_interval)


def _get_stop_signal():
    """
    Get stop signal for worker.
    Returns `SIGBREAK` on windows because `SIGSTP` doesn't exist on it
    """
    if sys.platform.startswith("win"):
        # SIGSTP doesn't exist on windows, so we use SIGBREAK instead
        return signal.SIGBREAK

    return signal.SIGTSTP


def create_and_run(subs, config):
    """
    Create and run a worker from a list of Subscription objects and a config
    while waiting forever, until the process is stopped.

    We stop a worker process on:
    - SIGINT
    - SIGTSTP

    :param subs: List :class:`~rele.subscription.Subscription`
    :param config: :class:`~rele.config.Config`
    """
    print(f"Configuring worker with {len(subs)} subscription(s)...")
    for sub in subs:
        print(f"  {sub}")
    worker = Worker(
        subs,
        config.gc_project_id,
        config.credentials,
        config.ack_deadline,
        config.threads_per_subscription,
    )

    # to allow killing runrele worker via ctrl+c
    signal.signal(signal.SIGINT, worker.stop)
    signal.signal(signal.SIGTERM, worker.stop)
    signal.signal(_get_stop_signal(), worker.stop)

    worker.run_forever()
