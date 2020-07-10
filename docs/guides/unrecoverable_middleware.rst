.. _unrecoverable_middleware:

Unrecoverable Middleware
========================

To acknowledge and ignore incompatible messages that your subscription is unable to handle, you can use the `UnrecoverableMiddleware`.

Usage
__________

First make sure the middleware is included in your Relé config.

.. code:: python

    # settings.py
    import rele
    from google.oauth2 import service_account

    RELE = {
        'GC_CREDENTIALSGC_CREDENTIALS_PATH': 'credentials.json',
        'GC_PROJECT_ID': 'photo-uploading-app',
        'MIDDLEWARE': ['rele.contrib.UnrecoverableMiddleWare']
    }
    config = rele.config.setup(RELE)

Then in your subscription handler if you encounter an incompatible message raise the `UnrecoverableException`. Your message will be `.acked()` and it will not be redelivered to your subscription.

.. code:: python

    from rele.contrib.unrecoverable_middleware import UnrecoverableException
    from rele import sub

    @sub(topic='photo-uploaded')
    def photo_uploaded(data, **kwargs):

      if data.get("required_property") is None:
          # Incompatible
          raise UnrecoverableException("required_property is required.")

      # Handle correct messages
