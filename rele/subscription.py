import json
import logging
import time

from django import db
from django.conf import settings

logger = logging.getLogger(__name__)


class Subscription:

    def __init__(self, func, topic, suffix=None):
        self._func = func
        self.topic = topic
        self.project_name = settings.BASE_DIR.split("/")[-1]
        self.name = f'{self.project_name}-{topic}'
        if suffix:
            self.name += f'-{suffix}'

    def __call__(self, data, **kwargs):
        self._func(data, **kwargs)

    def __str__(self):
        return f'{self.name} - {self._func.__name__}'


class Callback:

    def __init__(self, subscription, suffix=None):
        self._subscription = subscription
        self._suffix = suffix

    def __call__(self, message):
        start_time = time.time()
        db.close_old_connections()

        logger.debug(f'Start processing message for {self._subscription}',
                     extra={
                         'metrics': self._build_metrics('received')
                     })
        data = json.loads(message.data.decode('utf-8'))
        try:
            self._subscription(data, **dict(message.attributes))
        except Exception as e:
            logger.error(f'Exception raised while processing message '
                         f'for {self._subscription}: {str(e.__class__.__name__)}',
                         exc_info=True,
                         extra={
                             'metrics': self._build_metrics('failed', start_time)
                         })
        else:
            message.ack()
            logger.info(f'Successfully processed message for {self._subscription}',
                        extra={
                            'metrics': self._build_metrics('succeeded', start_time)
                        })
        finally:
            db.close_old_connections()

    def _build_metrics(self, status, start_processing_time=None):
        return {
            'name': 'subscriptions',
            'data': self._build_data_metrics(status, start_processing_time)
        }

    def _build_data_metrics(self, status, start_processing_time):
        result = {
            'agent': self._subscription.project_name,
            'topic': self._subscription.topic,
            'status': status,
            'subscription': self._subscription.name,
        }

        if start_processing_time is not None:
            end_processing_time = time.time()
            result['duration_seconds'] = round(
                end_processing_time - start_processing_time, 3)

        return result


def sub(topic, suffix=None):
    """Decorator function that makes declaring a PubSub Subscription simple.

    The Subscriber returned will automatically create and name
    the subscription for the topic.
    The subscription name will be the topic name prefixed by the project name.

    For example, if the topic name to subscribe too is `lets-tell-everyone`,
    the subscriber will be named `project-name-lets-tell-everyone`.

    Additionally, if a `suffix` param is added, the subscriber will be
    `project-name-lets-tell-everyone-my-suffix`.

    It is recommended to add **kwargs to your `sub` function. This will allow
    message attributes to be sent without breaking the subscriber implementation.

    Usage::

        @sub(topic='lets-tell-everyone', suffix='sub1')
        def purpose_1(data, **kwargs):
             pass

        @sub(topic='lets-tell-everyone', suffix='sub2')
        def purpose_2(data, **kwargs):
             pass

    :param topic: string The topic that is being subscribed to.
    :param suffix: string An options suffix to the subscription name.
                   Useful when you have two subscribers in the same project that
                   are subscribed to the same topic.
    :return: Subscription
    """

    def decorator(func):
        return Subscription(func=func, topic=topic, suffix=suffix)

    return decorator
