import importlib
import warnings
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from rele.config import Config
    from rele.subscription import Subscription

_middlewares: list["BaseMiddleware"] = []

default_middleware = ["rele.contrib.LoggingMiddleware"]
DEPRECATED_HOOKS = ["post_publish"]


def register_middleware(config: "Config", **kwargs: Any) -> None:
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


def run_middleware_hook(hook_name: str, *args: Any, **kwargs: Any) -> None:
    for middleware in _middlewares:
        if hook_name not in DEPRECATED_HOOKS or hasattr(middleware, hook_name):
            getattr(middleware, hook_name)(*args, **kwargs)


class WarnDeprecatedHooks(type):
    def __new__(cls, *args: Any, **kwargs: Any) -> type:
        x: type = super().__new__(cls, *args, **kwargs)
        for deprecated_hook in DEPRECATED_HOOKS:
            if hasattr(x, deprecated_hook):
                warnings.warn(
                    "The post_publish hook in the middleware is deprecated "
                    "and will be removed in future versions. Please substitute it with "
                    "the post_publish_success hook instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
        return x


class BaseMiddleware(metaclass=WarnDeprecatedHooks):
    """Base class for middleware.  The default implementations
    for all hooks are no-ops and subclasses may implement whatever
    subset of hooks they like.
    """

    def setup(self, config: "Config", **kwargs: Any) -> None:
        """Called when middleware is registered.
        :param config: Relé Config object
        """

    def pre_publish(self, topic: str, data: Any, attrs: dict[str, Any]) -> None:
        """Called before Publisher sends message.
        :param topic:
        :param data:
        :param attrs:
        """

    def post_publish_success(
        self, topic: str, data: Any, attrs: dict[str, Any]
    ) -> None:
        """Called after Publisher succesfully sends message.
        :param topic:
        :param data:
        :param attrs:
        """

    def post_publish_failure(
        self, topic: str, exception: Exception, message: Any
    ) -> None:
        """Called after publishing fails.
        :param topic:
        :param exception:
        :param message:
        """

    def pre_process_message(self, subscription: "Subscription", message: Any) -> None:
        """Called when the Worker receives a message.
        :param subscription:
        :param message:
        """

    def post_process_message(self) -> None:
        """Called after the Worker processes the message."""

    def post_process_message_success(
        self, subscription: "Subscription", start_time: float, message: Any
    ) -> None:
        """Called after the message has been successfully processed.
        :param subscription:
        :param start_time:
        :param message:
        """

    def post_process_message_failure(
        self,
        subscription: "Subscription",
        exception: Exception,
        start_time: float,
        message: Any,
    ) -> None:
        """Called after the message has been unsuccessfully processed.
        :param subscription:
        :param exception:
        :param start_time:
        :param message:
        """

    def pre_worker_start(self) -> None:
        """Called before the Worker process starts up."""

    def post_worker_start(self) -> None:
        """Called after the Worker process starts up."""

    def pre_worker_stop(self, subscriptions: list["Subscription"]) -> None:
        """Called before the Worker process shuts down."""

    def post_worker_stop(self) -> None:
        """Called after the Worker process shuts down."""
