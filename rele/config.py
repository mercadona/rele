from .middleware import register_middleware
from .publishing import init_global_publisher


def setup(setting):
    gc_project_id = setting.get('GC_PROJECT_ID')
    credentials = setting.get('GC_CREDENTIALS')

    init_global_publisher(gc_project_id, credentials)
    register_middleware(setting)
