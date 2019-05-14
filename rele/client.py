import logging
import os
from contextlib import suppress

from django.conf import settings
from google.api_core import exceptions
from google.cloud import pubsub_v1
from rest_framework.renderers import JSONRenderer

logger = logging.getLogger(__name__)

USE_EMULATOR = True if os.environ.get('PUBSUB_EMULATOR_HOST') else False


class Subscriber:

    def __init__(self):
        if USE_EMULATOR:
            self._client = pubsub_v1.SubscriberClient()
        else:
            self._client = pubsub_v1.SubscriberClient(
                credentials=settings.RELE_GC_CREDENTIALS)

    def create_subscription(self, subscription, topic):
        subscription_path = self._client.subscription_path(
            settings.RELE_GC_PROJECT_ID, subscription)
        topic_path = self._client.topic_path(
            settings.RELE_GC_PROJECT_ID, topic)

        with suppress(exceptions.AlreadyExists):
            self._client.create_subscription(
                name=subscription_path, topic=topic_path)

    def consume(self, subscription_name, callback):
        subscription_path = self._client.subscription_path(
            settings.RELE_GC_PROJECT_ID, subscription_name)
        return self._client.subscribe(subscription_path, callback=callback)


class Publisher:
    PUBLISH_TIMEOUT = 3.0

    def __init__(self):
        if USE_EMULATOR:
            self._client = pubsub_v1.PublisherClient()
        else:
            self._client = pubsub_v1.PublisherClient(
                credentials=settings.RELE_GC_CREDENTIALS)

    def publish(self, topic, data, blocking=False, **attrs):
        data = JSONRenderer().render(data)
        logger.info(f'Publishing to {topic}',
                    extra={'pubsub_publisher_data': data})
        topic_path = self._client.topic_path(
            settings.RELE_GC_PROJECT_ID, topic)
        future = self._client.publish(topic_path, data, **attrs)
        if not blocking:
            return future

        future.result(timeout=self.PUBLISH_TIMEOUT)
        return future
