import logging

from django.conf import settings

from rele.middleware import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    def __init__(self):
        self._logger = None

    def setup(self):
        self._logger = logging.getLogger(__name__)

    def pre_publish(self, topic, data, attrs):
        self._logger.info(f'Publishing to {topic}',
                          extra={
                              'pubsub_publisher_attrs': attrs,
                              'metrics': self._build_metrics(topic)
                          })

    def _build_metrics(self, topic):
        return {
            'name': 'publications',
            'data': {
                'agent': settings.BASE_DIR.split('/')[-1],
                'topic': topic,
            }
        }

    def pre_message_process(self, message):
        pass

    def post_message_process(self):
        pass

    def message_process_success(self):
        pass

    def message_process_failure(self):
        pass

    def pre_worker_start(self):
        pass

    def post_worker_start(self):
        pass

    def pre_worker_stop(self):
        pass

    def post_worker_stop(self):
        pass

