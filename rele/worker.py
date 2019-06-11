import logging
import sys

from django import db

from .client import Subscriber
from .subscription import Callback

logger = logging.getLogger(__name__)


class Worker:
    """A Worker manages the subscriptions which consume Google PubSub messages.

    Facilitates the creation of subscriptions if not already created,
    and the starting and stopping the consumption of them.

    :param subscriptions: list, List of :class:`rele.subscription.Subscription`
    """
    def __init__(self, subscriptions):
        self._subscriber = Subscriber()
        self._futures = []
        self._subscriptions = subscriptions

    def setup(self):
        """Create the subscriptions on a Google PubSub topic.

        If the subscription already exists, the subscription will not be re-created.
        Therefore, it is idempotent.
        """
        for subscription in self._subscriptions:
            self._subscriber.create_subscription(subscription.name,
                                                 subscription.topic)

    def start(self):
        """Begin consuming all subscriptions.

        When consuming a subscription, a `StreamingPullFuture` is returned from
        the Google PubSub client library. This future can be used to
        manage the background stream.

        The futures are stored so that they can be cancelled later on
        for a graceful shutdown of the worker.
        """
        for subscription in self._subscriptions:
            self._futures.append(self._subscriber.consume(
                subscription_name=subscription.name,
                callback=Callback(subscription)
            ))

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

        :param signal: Needed for signal.signal https://docs.python.org/3/library/signal.html#signal.signal
        :param frame: Needed for signal.signal https://docs.python.org/3/library/signal.html#signal.signal
        """
        logger.info(f'Cleaning up {len(self._futures)} subscription(s)...')
        for future in self._futures:
            future.cancel()

        db.connections.close_all()
        sys.exit(0)
