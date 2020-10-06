from rele import config, discover

from .client import Publisher

_publisher = None


def init_global_publisher(config):
    global _publisher
    if not _publisher:
        _publisher = Publisher(
            gc_project_id=config.gc_project_id,
            credentials=config.credentials,
            encoder=config.encoder,
            timeout=config.publisher_timeout,
        )
    return _publisher


def publish(topic, data, **kwargs):
    """Shortcut method to publishing data to PubSub.

    This is a shortcut method that instantiates the Publisher if not already
    instantiated in the process. This is to ensure that the Publisher remains a
    Singleton class.

    Usage::

        import rele

        def myfunc():
            # ...
            rele.publish(topic='lets-tell-everyone',
                         data={'foo': 'bar'},
                         myevent='arrival')

    :param topic: str PubSub topic name
    :param data: dict-like Data to be sent as the message.
    :param timeout: float. Default None, falls back to RELE['PUBLISHER_TIMEOUT'] value
    :param blocking: boolean. Default False
    :param kwargs: Any optional key-value pairs that are included as attributes
        in the message
    :return: None
    """
    if not _publisher:
        settings, _ = discover.sub_modules()
        if not hasattr(settings, "RELE"):
            raise ValueError("Config setup not called and settings module not found.")

        config.setup(settings.RELE)

    _publisher.publish(topic, data, **kwargs)
