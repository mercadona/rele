Basic Usage
===========


Configuration
_____________

In order to get started using Relé, we must have a PubSub topic in which to publish.
Via the `Google Cloud Console <https://cloud.google.com/pubsub/docs/quickstart-console>`_
we create one, named ``photo-upload``.

To authenticate our pubslisher and subscriber, follow the
`Google guide <https://cloud.google.com/pubsub/docs/authentication>`_ on
how to obtain your authentication account.

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

Once the topic is created and our Django application has the proper configuration defined
in :doc:`settings.RELE <../api/settings>`, we can start publishing to that topic.


.. code:: python

    import rele

    data = {'google_bucket_location': '/google-bucket/photos/123.jpg'}

    rele.publish(topic='photo-uploaded', data=data)

To publish we simple pass in the topic to which we want our data to publish too, followed by
a valid json serializable Python object.

.. note:: If you want to publish other types of objects, you may configure the encoder class.

If you need to pass in additional attributes to the Message object, you can simply add ``kwargs``:

.. code:: python

    rele.publish(topic='photo-uploaded',
                 data=data,
                 type='profile',
                 rotation='landscape')


Subscribing
___________

Once we can publish to a topic, we can subscribe to the topic from a worker instance.
In an app directory, we create our sub function within our subs.py file.

.. code:: python

    from rele import sub

    @sub(topic='photo-uploaded')
    def photo_uploaded(data, **kwargs):
        print(f"Someone has uploaded an image to our service,
                and we stored it at {data['google_bucket_location'}.")

Once the sub is created, we can start our worker by running ``python manage.py runrele``.

Additionally, if you added message attributes to your Message, you can access them via the
`kwargs` argument:

.. code:: python

    @sub(topic='photo-uploaded')
    def photo_uploaded(data, **kwargs):
        print(f"Someone has uploaded an image to our service,
                and we stored it at {data['google_bucket_location'}.
                It is a {kwargs['type']} picture with the
                rotation {kwargs['rotation']}")

Consuming
_________

The Relé worker process will autodiscover any properly decorated sub
function in the subs.py filed and create the subscription for us.
Once the process is up and running, we can publish and consume.
