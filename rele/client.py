import json
import logging
import os
import time
from contextlib import suppress

from google.api_core import exceptions
from google.cloud import pubsub_v1
from rest_framework.utils import encoders

from rele.middleware import run_middleware_hook

logger = logging.getLogger(__name__)

USE_EMULATOR = True if os.environ.get('PUBSUB_EMULATOR_HOST') else False


class Subscriber:
    DEFAULT_ACK_DEADLINE = 60

    def __init__(self, gc_project_id, credentials):
        self._gc_project_id = gc_project_id
        if USE_EMULATOR:
            self._client = pubsub_v1.SubscriberClient()
        else:
            self._client = pubsub_v1.SubscriberClient(credentials=credentials)

    def get_default_ack_deadline(self):
        return int(os.environ.get('DEFAULT_ACK_DEADLINE',
                                  self.DEFAULT_ACK_DEADLINE))

    def create_subscription(
            self, subscription, topic, ack_deadline_seconds=None):
        ack_deadline_seconds = ack_deadline_seconds or \
            self.get_default_ack_deadline()

        subscription_path = self._client.subscription_path(
            self._gc_project_id, subscription)
        topic_path = self._client.topic_path(self._gc_project_id, topic)

        with suppress(exceptions.AlreadyExists):
            self._client.create_subscription(
                name=subscription_path,
                topic=topic_path,
                ack_deadline_seconds=ack_deadline_seconds)

    def consume(self, subscription_name, callback):
        subscription_path = self._client.subscription_path(
            self._gc_project_id, subscription_name)
        return self._client.subscribe(subscription_path, callback=callback)


class Publisher:
    """The Publisher Class

    Wraps the Google Cloud Publisher Client and handles.

    It is important that this class remains a Singleton class in the process.
    Otherwise, a memory leak will occur. To avoid this, it is strongly
    recommended to use the :meth:`~rele.publishing.publish` method.

    If the setting `USE_EMULATOR` evaluates to True, the Publisher Client will
    not have any credentials assigned.

    :param gc_project_id: string Google Cloud Project ID.
    :param credentials: string Google Cloud Credentials.
    :param timeout: integer, default 3.0 seconds.
    """
    def __init__(self, gc_project_id, credentials, timeout=3.0):
        self._gc_project_id = gc_project_id
        self._timeout = timeout
        if USE_EMULATOR:
            self._client = pubsub_v1.PublisherClient()
        else:
            self._client = pubsub_v1.PublisherClient(credentials=credentials)

    def publish(self, topic, data, blocking=False, **attrs):
        """Publishes message to Google PubSub topic.

        Usage::

            publisher = Publisher()
            publisher.publish('topic_name', {'foo': 'bar'})

        By default, this method is non-blocking, meaning that the method does
        not wait for the future to be returned.

        If you would like to wait for the future so you can track the message
        later, you can:

        Usage::

            publisher = Publisher()
            future = publisher.publish('topic_name', {'foo': 'bar'}, blocking=True) # noqa

        However, it should be noted that using `blocking=True` may incur a
        significant performance hit.

        In addition, the method adds a timestamp `published_at` to the
        message attrs using `epoch floating point number
        <https://docs.python.org/3/library/time.html#time.time>`_.

        :param topic: string topic to publish the data.
        :param data: dict with the content of the message.
        :param blocking: boolean, default False.
        :param attrs: Extra parameters to be published.
        :return: `Future <https://googleapis.github.io/google-cloud-python/latest/pubsub/subscriber/api/futures.html>`_  # noqa
        """

        attrs['published_at'] = str(time.time())
        run_middleware_hook('pre_publish', topic, data, attrs)
        payload = json.dumps(data, cls=encoders.JSONEncoder).encode('utf-8')
        topic_path = self._client.topic_path(self._gc_project_id, topic)
        future = self._client.publish(topic_path, payload, **attrs)
        if not blocking:
            return future

        future.result(timeout=self._timeout)
        run_middleware_hook('post_publish', topic)
        return future
