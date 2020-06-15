import importlib
import os

from .client import DEFAULT_ACK_DEADLINE, DEFAULT_ENCODER_PATH, get_google_defaults
from .middleware import default_middleware, register_middleware
from .publishing import init_global_publisher
from .subscription import Subscription


class Config:
    """Configuration class.

    The settings.RELE dictionary will be parsed into an easily
    accessible object containing all the necessary constants.

    If no middleware is set, the *default_middleware* will be added.

    :param setting: dict :ref:`settings <_settings>`
    """

    def __init__(self, setting):
        if (
            setting.get("GC_PROJECT_ID") is None
            or setting.get("GC_CREDENTIALS") is None
        ):
            credentials, project = get_google_defaults()

        self.credentials = setting.get("GC_CREDENTIALS") or credentials
        self.gc_project_id = setting.get("GC_PROJECT_ID") or project
        self.app_name = setting.get("APP_NAME")
        self.sub_prefix = setting.get("SUB_PREFIX")
        self.middleware = setting.get("MIDDLEWARE", default_middleware)
        self.ack_deadline = setting.get(
            "ACK_DEADLINE",
            os.environ.get("DEFAULT_ACK_DEADLINE", DEFAULT_ACK_DEADLINE),
        )
        self._encoder_path = setting.get("ENCODER_PATH", DEFAULT_ENCODER_PATH)
        self.publisher_timeout = setting.get("PUBLISHER_TIMEOUT", 3.0)
        self.threads_per_subscription = setting.get("THREADS_PER_SUBSCRIPTION", 2)
        self.filter_by = setting.get("FILTER_SUBS_BY")

    @property
    def encoder(self):
        module_name, class_name = self._encoder_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)


def setup(setting=None, **kwargs):
    if setting is None:
        setting = {}

    config = Config(setting)
    init_global_publisher(config)
    register_middleware(config, **kwargs)
    return config


def load_subscriptions_from_paths(sub_module_paths, sub_prefix=None, filter_by=None):

    subscriptions = []
    for sub_module_path in sub_module_paths:
        sub_module = importlib.import_module(sub_module_path)
        for attr_name in dir(sub_module):
            attribute = getattr(sub_module, attr_name)
            try:
                if isinstance(attribute, Subscription):
                    subscription = attribute
                elif issubclass(attribute, Subscription):
                    subscription = attribute()
                else:
                    continue
            except TypeError:
                continue
            if sub_prefix and not subscription.prefix:
                subscription.set_prefix(sub_prefix)

            if filter_by and not subscription.filter_by:
                subscription.set_filters(filter_by)

            subscriptions.append(subscription)
    return subscriptions
