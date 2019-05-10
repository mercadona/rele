import json
import logging
from contextlib import suppress

from django.conf import settings
from google.api_core import exceptions
from google.cloud import pubsub_v1

logger = logging.getLogger(__name__)


class Subscriber:

    def __init__(self):
        self._client = pubsub_v1.SubscriberClient(
            credentials=settings.RELE_GC_CREDENTIALS)

    def create_subscription(self, subscription, topic):
        subscription_path = self._client.subscription_path(
            settings.GC_PROJECT_ID, subscription)
        topic_path = self._client.topic_path(
            settings.RELE_GC_PROJECT_ID, topic)

        with suppress(exceptions.AlreadyExists):
            self._client.create_subscription(
                name=subscription_path, topic=topic_path)

    def subscribe(self, subscription_name, callback):
        subscription_path = self._client.subscription_path(
            settings.GC_PROJECT_ID, subscription_name)
        return self._client.subscribe(subscription_path, callback=callback)


class _PublisherSingleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(_PublisherSingleton, cls).__call__(
                *args, **kwargs)
        return cls._instance


class Publisher(metaclass=_PublisherSingleton):
    PUBLISH_TIMEOUT = 2.0

    def __init__(self):
        self._client = pubsub_v1.PublisherClient(
            credentials=settings.RELE_GC_CREDENTIALS)

    def publish(self, topic, data, **attrs):
        data = json.dumps(data).encode()
        logger.info(f'Publishing to {topic}',
                    extra={'pubsub_publisher_data': data})
        topic_path = self._client.topic_path(
            settings.RELE_GC_PROJECT_ID, topic)
        future = self._client.publish(topic_path, data, **attrs)
        try:
            future.result(timeout=self.PUBLISH_TIMEOUT)
        except Exception:
            logger.error('Exception while publishing to %s', topic,
                         exc_info=True, extra={'pubsub_data': data})
            return False
        return True
