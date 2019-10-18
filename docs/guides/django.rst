.. _django_integration:

Django Integration
==================

.. note::
    This guide simply points out the differences between standalone Relé and
    the Django integration. The basics about publishing and subscribing are described
    in the :ref:`basics` section.

Publishing
__________

To configure Relé, our settings may look something like:

.. code:: python

    from google.oauth2 import service_account
    RELE = {
        'GC_CREDENTIALS': service_account.Credentials.from_service_account_file(
            'photo_project/settings/dummy-credentials.json'
        ),
        'GC_PROJECT_ID': 'photo-imaging',
        'MIDDLEWARE': [
            'rele.contrib.LoggingMiddleware',
            'rele.contrib.DjangoDBMiddleware',
        ],
        'APP_NAME': 'photo-imaging',
    }

The only major difference here is that we are using the ``rele.contrib.DjangoDBMiddleware``.
This is important to properly close DB connections.

.. important::
    If you plan on having your subscriber connect to the database, it is vital that
    the Django settings.CONN_MAX_AGE is set to 0.


Once the topic is created and our Django application has the proper configuration defined
in :ref:`settings`, we can start publishing to that topic.


Subscribing
___________

:ref:`subscribing` follows the same method as before.


Consuming
_________

Unlike what is described in :ref:`consuming`, the Django integration provides a very convenient
command.

By running ``python manage.py runrele``, worker process will autodiscover any properly decorated sub
function in the subs.py filed and create the subscription for us.

Once the process is up and running, we can publish and consume.
