import json
import logging
import time
from collections.abc import Iterable
from inspect import getfullargspec, getmodule

from .middleware import run_middleware_hook

logger = logging.getLogger(__name__)


class Subscription:
    """The Subscription class

    In addition to using the ``@sub`` decorator, it is possible to subclass
    the Subscription.

    For example::

        from rele import Subscription

        class DoSomethingSub(Subscription):
            topic = 'photo-uploaded'

            def __init__(self):
                self._func = self.callback_func
                super().__init__(self._func, self.topic)

            def callback_func(self, data, **kwargs):
                print(data["id"])

    If ``rele-cli run`` is used, the ``DoSomethingSub`` will be a valid subscription
    and registered on Google Cloud.

    """

    def __init__(self, func, topic, prefix="", suffix="", filter_by=None):
        self._func = func
        self.topic = topic
        self._prefix = prefix
        self._suffix = suffix
        self._filters = self._init_filters(filter_by)

    def _init_filters(self, filter_by):
        if filter_by and not (
            callable(filter_by)
            or (
                isinstance(filter_by, Iterable)
                and all(callable(filter) for filter in filter_by)
            )
        ):
            raise ValueError("Filter_by must be a callable or a list of callables.")

        if isinstance(filter_by, Iterable):
            return filter_by
        elif filter_by:
            return [filter_by]

        return None

    @property
    def name(self):
        name_parts = [self._prefix, self.topic, self._suffix]
        return "-".join(filter(lambda x: x, name_parts))

    @property
    def prefix(self):
        return self._prefix

    def set_prefix(self, prefix):
        self._prefix = prefix

    @property
    def filter_by(self):
        return self._filters

    def set_filters(self, filter_by):
        self._filters = filter_by

    def __call__(self, data, **kwargs):
        if "published_at" in kwargs:
            kwargs["published_at"] = float(kwargs["published_at"])

        if self._any_filter_returns_false(kwargs):
            return

        return self._func(data, **kwargs)

    def __str__(self):
        return f"{self.name} - {self._func.__name__}"

    def _any_filter_returns_false(self, kwargs):
        if not self._filters:
            return False

        return not all(filter(kwargs) for filter in self._filters)


class Callback:
    def __init__(self, subscription, suffix=None):
        self._subscription = subscription
        self._suffix = suffix

    def __call__(self, message):
        run_middleware_hook("pre_process_message", self._subscription, message)
        start_time = time.time()

        try:
            data = json.loads(message.data.decode("utf-8"))
        except json.JSONDecodeError as e:
            message.ack()
            run_middleware_hook(
                "post_process_message_failure",
                self._subscription,
                e,
                start_time,
                message,
            )
            run_middleware_hook("post_process_message")
            return

        try:
            res = self._subscription(data, **dict(message.attributes))
        except Exception as e:
            run_middleware_hook(
                "post_process_message_failure",
                self._subscription,
                e,
                start_time,
                message,
            )
        else:
            message.ack()
            run_middleware_hook(
                "post_process_message_success",
                self._subscription,
                start_time,
                message,
            )
            return res
        finally:
            run_middleware_hook("post_process_message")


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
    :param filter_by: Union[function, list] An optional function or tuple of
                      functions that filters the messages to be processed by
                      the sub regarding their attributes.
    :return: :class:`~rele.subscription.Subscription`
    """

    def decorator(func):
        args_spec = getfullargspec(func)
        if len(args_spec.args) != 1 or not args_spec.varkw:
            raise RuntimeError(
                f"Subscription function {func.__module__}.{func.__name__} is not valid. "
                "The function must have one argument and accept keyword arguments."
            )

        if getmodule(func).__name__.split(".")[-1] != "subs":
            logger.warning(
                f"Subscription function {func.__module__}.{func.__name__} is "
                "outside a subs module that will not be discovered."
            )

        return Subscription(
            func=func,
            topic=topic,
            prefix=prefix,
            suffix=suffix,
            filter_by=filter_by,
        )

    return decorator
