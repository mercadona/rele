import importlib
import os
import warnings

from google.oauth2 import service_account

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
        self._project_id = setting.get("GC_PROJECT_ID")
        self.gc_credentials_path = setting.get("GC_CREDENTIALS_PATH")
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
        self._credentials = None

    @property
    def encoder(self):
        module_name, class_name = self._encoder_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    @property
    def credentials(self):
        if self.gc_credentials_path:
            self._credentials = service_account.Credentials.from_service_account_file(
                self.gc_credentials_path
            )
        else:
            credentials, __ = get_google_defaults()
            self._credentials = credentials
        return self._credentials

    @property
    def gc_project_id(self):
        if self._project_id:
            warnings.warn(
                "GC_PROJECT_ID is deprecated in a future release.", DeprecationWarning
            )
            return self._project_id
        elif self.credentials:
            return self.credentials.project_id
        else:
            return None


def setup(setting=None, **kwargs):
    if setting is None:
        setting = {}

    config = Config(setting)
    init_global_publisher(config)
    register_middleware(config, **kwargs)
    return config


def subscription_from_attribute(attribute):
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


def load_subscriptions_from_paths(sub_module_paths, sub_prefix=None, filter_by=None):

    subscriptions = []
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

            subscriptions.append(subscription)
    return subscriptions
