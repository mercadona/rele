from .middleware import register_middleware
from .publishing import init_global_publisher


def setup(config):
    gc_project_id = config.get('GC_PROJECT_ID')
    credentials = config.get('GC_CREDENTIALS')

    init_global_publisher(gc_project_id, credentials)
    register_middleware(config)
