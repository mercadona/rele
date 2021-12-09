import json
import logging
import os
import time
from concurrent.futures import TimeoutError
from contextlib import suppress

import google.auth
from google.api_core import exceptions
from google.cloud import pubsub_v1

from rele.middleware import run_middleware_hook

logger = logging.getLogger(__name__)

USE_EMULATOR = True if os.environ.get("PUBSUB_EMULATOR_HOST") else False
DEFAULT_ENCODER_PATH = "json.JSONEncoder"
DEFAULT_ACK_DEADLINE = 60


def get_google_defaults():
    try:
        credentials, project = google.auth.default()
        return credentials, project
    except google.auth.exceptions.DefaultCredentialsError:
        return None, None


class Subscriber:
    """The Subscriber Class.

    For convenience, this class wraps the creation and consumption of a topic
    subscription.

    :param gc_project_id: str :ref:`settings_project_id` .
    :param credentials: obj :meth:`~rele.config.Config.credentials`.
    :param default_ack_deadline: int Ack Deadline defined in settings
    """

    def __init__(self, gc_project_id, credentials, default_ack_deadline=None):
        self._gc_project_id = gc_project_id
        self._ack_deadline = default_ack_deadline or DEFAULT_ACK_DEADLINE
        self.credentials = credentials if not USE_EMULATOR else None
        self._client = pubsub_v1.SubscriberClient(credentials=credentials)

    def create_subscription(self, subscription, topic):
        """Handles creating the subscription when it does not exists.

        This makes it easier to deploy a worker and forget about the
        subscription side of things. The subscription must
        have a topic to subscribe to. Which means that the topic must be
        created manually before the worker is started.

        :param subscription: str Subscription name
        :param topic: str Topic name to subscribe
        """
        subscription_path = self._client.subscription_path(
            self._gc_project_id, subscription
        )
        topic_path = self._client.topic_path(self._gc_project_id, topic)

        with suppress(exceptions.AlreadyExists):
            try:
                self._create_subscription(subscription_path, topic_path)
            except exceptions.NotFound:
                logger.warning(
                    "Cannot subscribe to a topic that does not exist."
                    f"Creating {topic_path}..."
                )
                topic = self._create_topic(topic_path)
                logger.info(f"Topic {topic.name} created.")
                self._create_subscription(subscription_path, topic_path)

    def _create_topic(self, topic_path):
        publisher_client = pubsub_v1.PublisherClient(credentials=self.credentials)
        return publisher_client.create_topic(request={"name": topic_path})

    def _create_subscription(self, name, topic):
        self._client.create_subscription(
            name=name,
            topic=topic,
            ack_deadline_seconds=self._ack_deadline,
        )

    def consume(self, subscription_name, callback, scheduler):
        """Begin listening to topic from the SubscriberClient.

        :param subscription_name: str Subscription name
        :param callback: Function which act on a topic message
        :param scheduler: `Thread pool-based scheduler. <https://googleapis.dev/python/pubsub/latest/subscriber/api/scheduler.html?highlight=threadscheduler#google.cloud.pubsub_v1.subscriber.scheduler.ThreadScheduler>`_  # noqa
        :return: `Future <https://googleapis.github.io/google-cloud-python/latest/pubsub/subscriber/api/futures.html>`_  # noqa
        """
        subscription_path = self._client.subscription_path(
            self._gc_project_id, subscription_name
        )
        return self._client.subscribe(
            subscription_path, callback=callback, scheduler=scheduler
        )


class Publisher:
    """The Publisher Class

    Wraps the Google Cloud Publisher Client and handles encoding of the data.

    It is important that this class remains a Singleton class in the process.
    Otherwise, a memory leak will occur. To avoid this, it is strongly
    recommended to use the :meth:`~rele.publishing.publish` method.

    If the setting `USE_EMULATOR` evaluates to True, the Publisher Client will
    not have any credentials assigned.

    :param gc_project_id: string Google Cloud Project ID.
    :param credentials: string Google Cloud Credentials.
    :param encoder: A valid `json.encoder.JSONEncoder subclass <https://docs.python.org/3/library/json.html#json.JSONEncoder>`_  # noqa
    :param timeout: float, default :ref:`settings_publisher_timeout`
    """

    def __init__(self, gc_project_id, credentials, encoder, timeout):
        self._gc_project_id = gc_project_id
        self._timeout = timeout
        self._encoder = encoder
        if USE_EMULATOR:
            self._client = pubsub_v1.PublisherClient()
        else:
            self._client = pubsub_v1.PublisherClient(credentials=credentials)

    def publish(
        self, topic, data, blocking=False, timeout=None, raise_exception=True, **attrs
    ):
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
            future = publisher.publish('topic_name', {'foo': 'bar'}, blocking=True, timeout=10.0) # noqa

        However, it should be noted that using `blocking=True` may incur a
        significant performance hit.

        In addition, the method adds a timestamp `published_at` to the
        message attrs using `epoch floating point number
        <https://docs.python.org/3/library/time.html#time.time>`_.

        :param topic: string topic to publish the data.
        :param data: dict with the content of the message.
        :param blocking: boolean
        :param timeout: float, default None falls back to :ref:`settings_publisher_timeout`
        :param raise_exception: boolean. If True, exceptions coming from PubSub will be raised
        :param attrs: additional string parameters to be published.
        :return: `Future <https://googleapis.github.io/google-cloud-python/latest/pubsub/subscriber/api/futures.html>`_  # noqa
        """

        attrs["published_at"] = str(time.time())
        run_middleware_hook("pre_publish", topic, data, attrs)
        payload = json.dumps(data, cls=self._encoder).encode("utf-8")
        topic_path = self._client.topic_path(self._gc_project_id, topic)
        future = self._client.publish(topic_path, payload, **attrs)
        if not blocking:
            return future

        try:
            future.result(timeout=timeout or self._timeout)
        except TimeoutError as e:
            run_middleware_hook("post_publish_failure", topic, e, data)
            if raise_exception:
                raise e
        else:
            run_middleware_hook("post_publish_success", topic, data, attrs)

            # DEPRECATED
            run_middleware_hook("post_publish", topic)

        return future
