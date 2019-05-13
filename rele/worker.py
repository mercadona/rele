import logging
import sys

from django import db

from .client import Subscriber
from .subscription import Callback

logger = logging.getLogger(__name__)


class Worker:

    def __init__(self, subscriptions):
        self._subscriber = Subscriber()
        self._futures = []
        self._subscriptions = subscriptions

    def setup(self):
        for subscription in self._subscriptions:
            self._subscriber.create_subscription(subscription.name,
                                                 subscription.topic)

    def start(self):
        for subscription in self._subscriptions:
            self._futures.append(self._subscriber.consume(
                subscription_name=subscription.name,
                callback=Callback(subscription)
            ))

    def stop(self, signal=None, frame=None):
        logger.info(f'Cleaning up {len(self._futures)} subscription(s)...')
        for future in self._futures:
            future.cancel()

        db.connections.close_all()
        sys.exit(0)
