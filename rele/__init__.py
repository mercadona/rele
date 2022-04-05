__version__ = "1.3.0"

try:
    import django
except ImportError:
    pass
else:
    if django.__version__ < "3.2":
        default_app_config = "rele.apps.ReleConfig"

from .client import Publisher, Subscriber  # noqa
from .config import setup  # noqa
from .publishing import publish  # noqa
from .subscription import Callback, Subscription, sub  # noqa
from .worker import Worker  # noqa
