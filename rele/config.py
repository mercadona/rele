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
