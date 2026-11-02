.. _retryable_middleware:

Retryable Middleware
====================

To ask Pub/Sub for an immediate redelivery of a message your subscription could not handle right now (for example, because a downstream service is temporarily unavailable), you can use the ``RetryableMiddleWare``. It is the counterpart of the :ref:`unrecoverable_middleware`: that one acknowledges a message to discard it, this one negatively acknowledges (``nack``) it to retry it.

By default, when a subscription raises an exception the message is neither acked nor nacked, and Pub/Sub redelivers it only once the acknowledgement deadline expires. This middleware is opt-in: nothing changes unless you add it to ``MIDDLEWARE``.

Usage
_____

First make sure the middleware is included in your Relé config.

.. code:: python

    # settings.py
    import rele

    RELE = {
        'GC_CREDENTIALS_PATH': 'credentials.json',
        'MIDDLEWARE': ['rele.contrib.RetryableMiddleWare']
    }
    config = rele.config.setup(RELE)

Then in your subscription handler, raise ``RetryableException`` when you want the message to be redelivered. Your message will be ``.nacked()``. Any other exception is left untouched.

.. code:: python

    from rele.contrib.retryable_middleware import RetryableException
    from rele import sub

    @sub(topic='photo-uploaded')
    def photo_uploaded(data, **kwargs):

      if not storage_is_available():
          # Try again
          raise RetryableException("storage is unavailable.")

      # Handle the message

.. warning::

    Without a ``DEFAULT_RETRY_POLICY``, a nacked message is redelivered immediately, so a subscription that keeps raising ``RetryableException`` can flood your subscriber with redeliveries. Configure a retry policy with exponential backoff (see :doc:`../settings`) when using this middleware:

    .. code:: python

        from rele.retry_policy import RetryPolicy

        RELE = {
            'GC_CREDENTIALS_PATH': 'credentials.json',
            'MIDDLEWARE': ['rele.contrib.RetryableMiddleWare'],
            'DEFAULT_RETRY_POLICY': RetryPolicy(minimum_backoff=10, maximum_backoff=600),
        }
