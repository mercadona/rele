import json
import logging
import os
from contextlib import suppress

from django.conf import settings
from google.api_core import exceptions
from google.cloud import pubsub_v1
from rest_framework.utils import encoders

logger = logging.getLogger(__name__)

USE_EMULATOR = True if os.environ.get('PUBSUB_EMULATOR_HOST') else False


class Subscriber:

    def __init__(self, gc_project_id, credentials):
        self._gc_project_id = gc_project_id
        if USE_EMULATOR:
            self._client = pubsub_v1.SubscriberClient()
        else:
            self._client = pubsub_v1.SubscriberClient(credentials=credentials)

    def create_subscription(self, subscription, topic):
        subscription_path = self._client.subscription_path(
            self._gc_project_id, subscription)
        topic_path = self._client.topic_path(self._gc_project_id, topic)

        with suppress(exceptions.AlreadyExists):
            self._client.create_subscription(
                name=subscription_path, topic=topic_path)

    def consume(self, subscription_name, callback):
        subscription_path = self._client.subscription_path(
            self._gc_project_id, subscription_name)
        return self._client.subscribe(subscription_path, callback=callback)


class Publisher:

    def __init__(self, gc_project_id, credentials, timeout=3.0):
        self._gc_project_id = gc_project_id
        self._timeout = timeout
        if USE_EMULATOR:
            self._client = pubsub_v1.PublisherClient()
        else:
            self._client = pubsub_v1.PublisherClient(credentials=credentials)

    def publish(self, topic, data, blocking=False, **attrs):
        logger.info(f'Publishing to {topic}',
                    extra={
                        'pubsub_publisher_attrs': attrs,
                        'metrics': self._build_metrics(topic)
                    })
        payload = json.dumps(data, cls=encoders.JSONEncoder).encode('utf-8')
        topic_path = self._client.topic_path(self._gc_project_id, topic)
        future = self._client.publish(topic_path, payload, **attrs)
        if not blocking:
            return future

        future.result(timeout=self._timeout)
        return future

    def _build_metrics(self, topic):
        return {
            'name': 'publications',
            'data': {
                'agent': settings.BASE_DIR.split('/')[-1],
                'topic': topic,
            }
        }
