import importlib

_middlewares = []


def register_middleware(paths):
    global _middlewares
    for path in paths:
        middleware = importlib.import_module(path)
        middleware.setup()
        _middlewares.append(middleware)


def run_middleware_hook(hook_name, *args, **kwargs):
    for middleware in _middlewares:
        getattr(middleware, hook_name)(*args, **kwargs)


class BaseMiddleware:

    def setup(self):
        pass

    def pre_publish(self):
        pass

    def post_publish(self):
        pass

    def pre_message_process(self, message, extra=None):
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
