from .middleware import register_middleware
from .publishing import init_global_publisher


def setup(gc_project_id, credentials, middleware_paths):
    init_global_publisher(gc_project_id, credentials)
    register_middleware(middleware_paths)
