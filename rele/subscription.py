import json
import logging
import time

from .middleware import run_middleware_hook

logger = logging.getLogger(__name__)


class Subscription:
    """The Subscription class

    """
    def __init__(self, func, topic, prefix='', suffix='', filter_by=None):
        self._func = func
        self.topic = topic
        self._prefix = prefix
        self._suffix = suffix
        self._filter_by = filter_by or (lambda **_: True)

    @property
    def name(self):
        name_parts = [self._prefix, self.topic, self._suffix]
        return '-'.join(filter(lambda x: x, name_parts))

    @property
    def prefix(self):
        return self._prefix

    def set_prefix(self, prefix):
        self._prefix = prefix

    def __call__(self, data, **kwargs):
        if 'published_at' in kwargs:
            kwargs['published_at'] = float(kwargs['published_at'])

        if self._filter_by(**kwargs):
            return self._func(data, **kwargs)

        return None

    def __str__(self):
        return f'{self.name} - {self._func.__name__}'


class Callback:

    def __init__(self, subscription, suffix=None):
        self._subscription = subscription
        self._suffix = suffix

    def __call__(self, message):
        run_middleware_hook('pre_process_message', self._subscription)
        start_time = time.time()

        data = json.loads(message.data.decode('utf-8'))

        try:
            res = self._subscription(data, **dict(message.attributes))
        except Exception as e:
            run_middleware_hook('post_process_message_failure',
                                self._subscription, e, start_time)
        else:
            message.ack()
            run_middleware_hook('post_process_message_success',
                                self._subscription, start_time)
            return res
        finally:
            run_middleware_hook('post_process_message')


def sub(topic, prefix=None, suffix=None, filter_by=None):
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

        @sub(topic='lets-tell-everyone', suffix='sub2')
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
    :return: :class:`~rele.subscription.Subscription`
    """

    def decorator(func):
        return Subscription(func=func,
                            topic=topic,
                            prefix=prefix,
                            suffix=suffix,
                            filter_by=filter_by)

    return decorator
