from .client import Publisher

_publisher = None


def publish(topic, data, **kwargs):
    global _publisher
    if not _publisher:
        _publisher = Publisher()
    _publisher.publish(topic, data, **kwargs)
