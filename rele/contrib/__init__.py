from .logging_middleware import LoggingMiddleware  # noqa

try:
    from .django_db_middleware import DjangoDBMiddleware  # noqa
except ImportError:
    pass
