import json
import logging
import time
from concurrent import futures

from .middleware import run_middleware_hook

logger = logging.getLogger(__name__)


class Subscription:
    """The Subscription class

    """

    def __init__(self, func, topic, thread_count, prefix="", suffix="", filter_by=None):
        self._func = func
        self.topic = topic
        self._prefix = prefix
        self._suffix = suffix
        self._filter_by = filter_by
        self._thread_count = thread_count
        self._scheduler = None

    @property
    def name(self):
        name_parts = [self._prefix, self.topic, self._suffix]
        return "-".join(filter(lambda x: x, name_parts))

    @property
    def prefix(self):
        return self._prefix

    def set_prefix(self, prefix):
        self._prefix = prefix

    @property
    def filter_by(self):
        return self._filter_by

    def set_filter_by(self, filter_by):
        self._filter_by = filter_by

    def __call__(self, data, **kwargs):
        if "published_at" in kwargs:
            kwargs["published_at"] = float(kwargs["published_at"])

        if self._filter_returns_false(kwargs):
            return

        return self._func(data, **kwargs)

    def __str__(self):
        return f"{self.name} - {self._func.__name__}"

    def _filter_returns_false(self, kwargs):
        return self._filter_by and not self._filter_by(kwargs)

    @property
    def scheduler(self):
        if self._scheduler:
            return self._scheduler
        executor_kwargs = {
            "thread_name_prefix": "ThreadPoolExecutor-ThreadScheduler"
        }
        self._scheduler = futures.ThreadPoolExecutor(
            max_workers=self._thread_count,
            **executor_kwargs
        )
        return self._scheduler


class Callback:
    def __init__(self, subscription, suffix=None):
        self._subscription = subscription
        self._suffix = suffix

    def __call__(self, message):
        run_middleware_hook("pre_process_message", self._subscription, message)
        start_time = time.time()

        data = json.loads(message.data.decode("utf-8"))

        try:
            res = self._subscription(data, **dict(message.attributes))
        except Exception as e:
            run_middleware_hook(
                "post_process_message_failure",
                self._subscription,
                e,
                start_time,
                message,
            )
        else:
            message.ack()
            run_middleware_hook(
                "post_process_message_success", self._subscription, start_time, message
            )
            return res
        finally:
            run_middleware_hook("post_process_message")


def sub(topic, prefix=None, suffix=None, filter_by=None, thread_count=10):
    """Decorator function that makes declaring a PubSub Subscription simple.

    The Subscriber returned will automatically create and name
    the subscription for the topic.
    The subscription name will be the topic name prefixed by the project name.

    For example, if the topic name to subscribe too is `lets-tell-everyone`,
    the subscriber will be named `project-name-lets-tell-everyone`.

    Additionally, if a `suffix` param is added, the subscriber will be
    `project-name-lets-tell-everyone-my-suffix`.

    It is recommended to add `**kwargs` to your `sub` function. This will allow
    message attributes to be sent without breaking the subscriber
    implementation.

    Usage::

        @sub(topic='lets-tell-to-alice', prefix='shop')
        def bob_purpose(data, **kwargs):
             pass

        @sub(topic='lets-tell-everyone', suffix='sub1')
        def purpose_1(data, **kwargs):
             pass

        @sub(topic='lets-tell-everyone', suffix='sub2', thread_count=1)
        def purpose_2(data, **kwargs):
             pass

        @sub(topic='photo-updated',
             filter_by=lambda **attrs: attrs.get('type') == 'landscape')
        def sub_process_landscape_photos(data, **kwargs):
            pass

    :param topic: string The topic that is being subscribed to.
    :param prefix: string An optional prefix to the subscription name.
                   Useful to namespace your subscription with your project name
    :param suffix: string An optional suffix to the subscription name.
                   Useful when you have two subscribers in the same project
                   that are subscribed to the same topic.
    :param filter_by: function An optional function that
                      filters the messages to be processed
                      by the sub regarding their attributes.
    :param thread_count: Thread count of subscriber. Default 10.
    :return: :class:`~rele.subscription.Subscription`
    """

    def decorator(func):
        return Subscription(
            func=func,
            topic=topic,
            prefix=prefix,
            suffix=suffix,
            filter_by=filter_by,
            thread_count=thread_count
        )

    return decorator
