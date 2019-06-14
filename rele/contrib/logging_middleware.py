import logging
import time

from rele.middleware import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):

    def __init__(self):
        self._logger = None

    def setup(self, config):
        self._logger = logging.getLogger(__name__)
        self._app_name = config.app_name

    def _build_data_metrics(
            self, subscription, status, start_processing_time=None):
        result = {
            'agent': self._app_name,
            'topic': subscription.topic,
            'status': status,
            'subscription': subscription.name,
        }

        if start_processing_time is not None:
            end_processing_time = time.time()
            result['duration_seconds'] = round(
                end_processing_time - start_processing_time, 3)

        return result

    def pre_publish(self, topic, data, attrs):
        self._logger.info(
            f'Publishing to {topic}',
            extra={
                'pubsub_publisher_attrs': attrs,
                'metrics': {
                    'name': 'publications',
                    'data': {
                        'agent': self._app_name,
                        'topic': topic,
                    }
                }
            })

    def pre_process_message(self, subscription):
        self._logger.debug(
            f'Start processing message for {subscription}',
            extra={
                'metrics': {
                    'name': 'subscriptions',
                    'data': self._build_data_metrics(subscription, 'received')
                }
            })

    def post_process_message_success(self, subscription, start_time):
        self._logger.info(
            f'Successfully processed message for {subscription}',
            extra={
                'metrics': {
                    'name': 'subscriptions',
                    'data': self._build_data_metrics(
                        subscription, 'succeeded', start_time)
                }
            })

    def post_process_message_failure(
            self, subscription, exception, start_time):
        self._logger.error(
            f'Exception raised while processing message '
            f'for {subscription}: {str(exception.__class__.__name__)}',
            exc_info=True,
            extra={
                'metrics': {
                    'name': 'subscriptions',
                    'data': self._build_data_metrics(
                        subscription, 'failed', start_time)
                }
            })

    def pre_worker_stop(self, subscriptions):
        self._logger.info(
            f'Cleaning up {len(subscriptions)} subscription(s)...')
