import importlib
import warnings

_middlewares = []

default_middleware = ["rele.contrib.LoggingMiddleware"]
DEPRECATED_HOOKS = ["post_publish"]


def register_middleware(config, **kwargs):
    paths = config.middleware
    global _middlewares
    _middlewares = []
    for path in paths:
        *module_parts, middleware_class = path.split(".")
        module_path = ".".join(module_parts)
        module = importlib.import_module(module_path)
        middleware = getattr(module, middleware_class)()
        middleware.setup(config, **kwargs)
        _middlewares.append(middleware)


def run_middleware_hook(hook_name, *args, **kwargs):
    for middleware in _middlewares:
        if hook_name not in DEPRECATED_HOOKS or hasattr(middleware, hook_name):
            getattr(middleware, hook_name)(*args, **kwargs)


class WarnDeprecatedHooks(type):
    def __new__(cls, *args, **kwargs):
        x = super().__new__(cls, *args, **kwargs)
        for deprecated_hook in DEPRECATED_HOOKS:
            if hasattr(x, deprecated_hook):
                warnings.warn(
                    "The post_publish hook in the middleware is deprecated "
                    "and will be removed in future versions. Please substitute it with "
                    "the post_publish_success hook instead.",
                    DeprecationWarning,
                )
        return x


class BaseMiddleware(metaclass=WarnDeprecatedHooks):
    """Base class for middleware.  The default implementations
    for all hooks are no-ops and subclasses may implement whatever
    subset of hooks they like.
    """

    def setup(self, config, **kwargs):
        """Called when middleware is registered.
        :param config: Relé Config object
        """

    def pre_publish(self, topic, data, attrs):
        """Called before Publisher sends message.
        :param topic:
        :param data:
        :param attrs:
        """

    def post_publish_success(self, topic, data, attrs):
        """Called after Publisher succesfully sends message.
        :param topic:
        :param data:
        :param attrs:
        """

    def post_publish_failure(self, topic, exception, message):
        """Called after publishing fails.
        :param topic:
        :param exception:
        :param message:
        """

    def pre_process_message(self, subscription, message):
        """Called when the Worker receives a message.
        :param subscription:
        :param message:
        """

    def post_process_message(self):
        """Called after the Worker processes the message."""

    def post_process_message_success(self, subscription, start_time, message):
        """Called after the message has been successfully processed.
        :param subscription:
        :param start_time:
        :param message:
        """

    def post_process_message_failure(
        self, subscription, exception, start_time, message
    ):
        """Called after the message has been unsuccessfully processed.
        :param subscription:
        :param exception:
        :param start_time:
        :param message:
        """

    def pre_worker_start(self):
        """Called before the Worker process starts up."""

    def post_worker_start(self):
        """Called after the Worker process starts up."""

    def pre_worker_stop(self, subscriptions):
        """Called before the Worker process shuts down."""

    def post_worker_stop(self):
        """Called after the Worker process shuts down."""
