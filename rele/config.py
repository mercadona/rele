import importlib

from rele.subscription import Subscription
from .middleware import register_middleware, default_middleware
from .publishing import init_global_publisher


class Config:

    def __init__(self, setting):
        self.gc_project_id = setting.get('GC_PROJECT_ID')
        self.credentials = setting.get('GC_CREDENTIALS')
        self.app_name = setting.get('APP_NAME')
        self.sub_prefix = setting.get('SUB_PREFIX')
        self.middleware = setting.get('MIDDLEWARE', default_middleware)


def setup(setting):
    config = Config(setting)
    init_global_publisher(config)
    register_middleware(config)
    return config


def load_subscriptions_from_paths(sub_module_paths, sub_prefix=None):
    subscriptions = []
    for sub_module_path in sub_module_paths:
        sub_module = importlib.import_module(sub_module_path)
        for attr_name in dir(sub_module):
            attribute = getattr(sub_module, attr_name)
            if isinstance(attribute, Subscription):
                if sub_prefix and not attribute.prefix:
                    attribute.set_prefix(sub_prefix)
                subscriptions.append(attribute)
    return subscriptions
