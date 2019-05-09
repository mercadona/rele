import json
import logging

from django import db
from django.conf import settings

logger = logging.getLogger(__name__)


class Subscription:

    def __init__(self, func, topic, suffix=None):
        self._func = func
        self.topic = topic
        self.name = f'{settings.BASE_DIR.split("/")[-1]}-{topic}'
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
        db.close_old_connections()

        logger.info(f'Start processing message for {self._subscription}')
        data = json.loads(message.data.decode('utf-8'))
        try:
            self._subscription(data, **dict(message.attributes))
        except Exception as e:
            logger.error(f'Exception raised while processing message '
                         f'for {self._subscription}: '
                         f'{str(e.__class__.__name__)}',
                         exc_info=True)
        else:
            message.ack()
            logger.info(f'Successfully processed message for '
                        f'{self._subscription}')
        finally:
            db.close_old_connections()


def sub(topic, suffix=None):

    def decorator(func):
        return Subscription(func=func, topic=topic, suffix=suffix)

    return decorator
