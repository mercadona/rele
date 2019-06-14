from .client import Publisher

_publisher = None


def init_global_publisher(config):
    global _publisher
    if not _publisher:
        _publisher = Publisher(config.gc_project_id, config.credentials)
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
    :param kwargs: Any optional key-value pairs that are included as attributes
        in the message
    :return: None
    """
    if not _publisher:
        raise ValueError('init_global_publisher must be called first.')
    _publisher.publish(topic, data, **kwargs)
