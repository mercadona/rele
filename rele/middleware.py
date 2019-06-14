import importlib

_middlewares = []


default_middleware = ['rele.contrib.LoggingMiddleware']


def register_middleware(config):
    paths = config.middleware
    global _middlewares
    _middlewares = []
    for path in paths:
        *module_parts, middleware_class = path.split('.')
        module_path = '.'.join(module_parts)
        module = importlib.import_module(module_path)
        middleware = getattr(module, middleware_class)()
        middleware.setup(config)
        _middlewares.append(middleware)


def run_middleware_hook(hook_name, *args, **kwargs):
    for middleware in _middlewares:
        getattr(middleware, hook_name)(*args, **kwargs)


class BaseMiddleware:

    def setup(self, config):
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

    def post_process_message_failure(
            self, subscription, exception, start_time):
        pass

    def pre_worker_start(self):
        pass

    def post_worker_start(self):
        pass

    def pre_worker_stop(self, subscriptions):
        pass

    def post_worker_stop(self):
        pass
