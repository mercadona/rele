import importlib
import json
import os
from collections.abc import Callable, Iterable
from typing import Any, cast

from google.oauth2 import service_account

from .client import (
    DEFAULT_ACK_DEADLINE,
    DEFAULT_BLOCKING,
    DEFAULT_ENCODER_PATH,
    get_google_defaults,
)
from .middleware import default_middleware, register_middleware
from .publishing import init_global_publisher
from .retry_policy import RetryPolicy
from .subscription import Subscription


class Config:
    """Configuration class.

    The settings.RELE dictionary will be parsed into an easily
    accessible object containing all the necessary constants.

    If no middleware is set, the *default_middleware* will be added.

    :param setting: dict :ref:`settings <_settings>`
    """

    def __init__(self, setting: dict[str, Any]) -> None:
        self._gc_project_id: str | None = setting.get("GC_PROJECT_ID")
        self.gc_credentials_path: str | None = setting.get("GC_CREDENTIALS_PATH")
        self.gc_storage_region: str | list[str] | None = setting.get(
            "GC_STORAGE_REGION",
            ["europe-southwest1", "europe-west1", "europe-west8", "europe-west9"],
        )
        self.app_name: str | None = setting.get("APP_NAME")
        self.sub_prefix: str | None = setting.get("SUB_PREFIX")
        self.middleware: list[str] = setting.get("MIDDLEWARE", default_middleware)
        self.ack_deadline: int = setting.get(
            "ACK_DEADLINE",
            os.environ.get("DEFAULT_ACK_DEADLINE", DEFAULT_ACK_DEADLINE),
        )
        self.publisher_blocking: bool = setting.get(
            "PUBLISHER_BLOCKING", DEFAULT_BLOCKING
        )
        self._encoder_path: str = setting.get("ENCODER_PATH", DEFAULT_ENCODER_PATH)
        self.publisher_timeout: float = setting.get("PUBLISHER_TIMEOUT", 3.0)
        self.threads_per_subscription: int = setting.get("THREADS_PER_SUBSCRIPTION", 2)
        self.filter_by: Callable[..., bool] | Iterable[Callable[..., bool]] | None = (
            setting.get("FILTER_SUBS_BY")
        )
        self._credentials: Any = None
        self.retry_policy: RetryPolicy | None = setting.get("DEFAULT_RETRY_POLICY")
        self.client_options: dict[str, Any] | None = setting.get("CLIENT_OPTIONS")

    @property
    def encoder(self) -> type[json.JSONEncoder]:
        module_name, class_name = self._encoder_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return cast(type[json.JSONEncoder], getattr(module, class_name))

    @property
    def credentials(self) -> Any:
        if self.gc_credentials_path:
            self._credentials = service_account.Credentials.from_service_account_file(  # type: ignore[no-untyped-call]
                self.gc_credentials_path
            )
        else:
            credentials, project_id = get_google_defaults()
            self._credentials = credentials
            if not self._gc_project_id:
                self._gc_project_id = project_id
        return self._credentials

    @property
    def gc_project_id(self) -> str | None:
        if self._gc_project_id:
            return self._gc_project_id
        elif self.credentials:
            return cast(str, self.credentials.project_id)
        else:
            return None


def setup(setting: dict[str, Any] | None = None, **kwargs: Any) -> Config:
    if setting is None:
        setting = {}

    config = Config(setting)
    init_global_publisher(config)
    register_middleware(config, **kwargs)
    return config


def is_same_subscription(
    a_subscription: Subscription | None, another_subscription: Subscription
) -> bool:
    return id(a_subscription) == id(another_subscription)


def is_subscription_registered(
    subscriptions: dict[str, Subscription], current_subscription: Subscription
) -> bool:
    registered_subscription = subscriptions.get(current_subscription.name)
    return is_same_subscription(registered_subscription, current_subscription)


def subscription_from_attribute(attribute: Any) -> Subscription | None:
    try:
        if isinstance(attribute, Subscription):
            subscription = attribute
        elif issubclass(attribute, Subscription):
            subscription = attribute()
        else:
            return None
    except TypeError:
        # If attribute is not a class, TypeError is raised when testing issubclass
        return None
    return subscription


def load_subscriptions_from_paths(
    sub_module_paths: list[str],
    sub_prefix: str | None = None,
    filter_by: Callable[..., bool] | Iterable[Callable[..., bool]] | None = None,
) -> list[Subscription]:
    subscriptions: dict[str, Subscription] = {}
    for sub_module_path in sub_module_paths:
        sub_module = importlib.import_module(sub_module_path)
        for attr_name in dir(sub_module):
            attribute = getattr(sub_module, attr_name)

            subscription = subscription_from_attribute(attribute)
            if not subscription:
                continue

            if sub_prefix and not subscription.prefix:
                subscription.set_prefix(sub_prefix)

            if filter_by and not subscription.filter_by:
                subscription.set_filters(filter_by)

            if is_subscription_registered(subscriptions, subscription):
                continue

            if subscription.name in subscriptions:
                found_func = subscriptions[subscription.name]._func
                func = subscription._func
                raise RuntimeError(
                    f"Duplicate subscription name found: {subscription.name}. "
                    f"Subs {func.__module__}.{func.__name__} and "
                    f"{found_func.__module__}.{found_func.__name__} collide."
                )

            subscriptions[subscription.name] = subscription
    return list(subscriptions.values())
