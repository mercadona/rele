import importlib

_middlewares = []


def register_middleware(paths):
    global _middlewares
    _middlewares = []
    for path in paths:
        *module_parts, middleware_class = path.split('.')
        module_path = '.'.join(module_parts)
        module = importlib.import_module(module_path)
        middleware = getattr(module, middleware_class)()
        middleware.setup()
        _middlewares.append(middleware)


def run_middleware_hook(hook_name, *args, **kwargs):
    for middleware in _middlewares:
        getattr(middleware, hook_name)(*args, **kwargs)


class BaseMiddleware:

    def setup(self):
        pass

    def pre_publish(self, topic, data, attrs):
        pass

    def post_publish(self, topic):
        pass

    def pre_process_message(self, subscription):
        pass

    def post_process_message(self):
        pass

    def post_process_message_success(self, subscription, start_time):
        pass

    def post_process_message_failure(self, subscription, exception, start_time):
        pass

    def pre_worker_start(self):
        pass

    def post_worker_start(self):
        pass

    def pre_worker_stop(self, subscriptions):
        pass

    def post_worker_stop(self):
        pass


# class DjangoDBMiddleware(BaseMiddleware):

#     def pre_message_process(self):
#         db.close_old_connections()


# class PrometheusMiddleware(BaseMiddleware):

#     def __init__(self, app_name):
#         self._app_name = app_name

#     def pre_message_publish(self):
#         logger.info(f'Publishing to {topic}',
#                     extra={
#                         'pubsub_publisher_attrs': attrs,
#                         'metrics': self._build_metrics(topic)
#                     })

#     def _build_metrics(self, topic):
#         return {
#             'name': 'publications',
#             'data': {
#                 'agent': self._app_name,
#                 'topic': topic,
#             }
#         }
