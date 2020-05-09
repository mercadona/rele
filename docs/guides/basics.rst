.. _basics:

First Steps
===========


Configuration
_____________

In order to get started using Relé, we must have a PubSub topic in which to publish.
Via the `Google Cloud Console <https://cloud.google.com/pubsub/docs/quickstart-console>`_
we create one, named ``photo-upload``.

To authenticate our publisher and subscriber, follow the
`Google guide <https://cloud.google.com/pubsub/docs/authentication>`_ on
how to obtain your authentication account.

Publishing
__________

To configure Relé, our settings may look something like:

.. code:: python

    # settings.py
    import rele
    from google.oauth2 import service_account

    RELE = {
        'GC_CREDENTIALS': service_account.Credentials.from_service_account_file(
            'credentials.json'
        ),
        'GC_PROJECT_ID': 'photo-uploading-app',
    }
    config = rele.config.setup(RELE)

.. code:: python

    # publisher.py

    import rele
    from settings import config  # we need this for initializing the global Publisher singleton

    data = {
        'customer_id': 123,
        'location': '/google-bucket/photos/123.jpg'
    }

    rele.publish(topic='photo-uploaded', data=data)

To publish data, we simply pass in the topic to which we want our data to be published to, followed by
a valid json serializable Python object.

.. note:: If you want to publish other types of objects, you may configure the encoder class.

If you need to pass in additional attributes to the Message object, you can simply add ``kwargs``.
These must all be strings:

.. code:: python

    rele.publish(topic='photo-uploaded',
                 data=data,
                 type='profile',
                 rotation='landscape')

.. note:: Anything other than a string attribute will result in a ``TypeError``.

.. _subscribing:

Subscribing
___________

Once we can publish to a topic, we can subscribe to the topic from a worker instance.
In an app directory, we create our sub function within our subs.py file.

.. code:: python

    # subs.py

    from rele import sub

    @sub(topic='photo-uploaded')
    def photo_uploaded(data, **kwargs):
        print(f"Customer {data['customer_id']} has uploaded an image to our service,
                and we stored it at {data['location'}.")

Additionally, if you added message attributes to your Message, you can access them via the
`kwargs` argument:

.. code:: python

    @sub(topic='photo-uploaded')
    def photo_uploaded(data, **kwargs):
        print(f"Customer {data['customer_id']} has uploaded an image to our service,
                and we stored it at {data['location'}.
                It is a {kwargs['type']} picture with the
                rotation {kwargs['rotation']}")


Message attributes
------------------

It might be helpful to access particular message attributes in your
subscriber. One attribute that _rele_ adds by default is `published_at`.
To access this attribute you can use `kwargs` keyword.

.. code:: python

    @sub(topic='photo-uploaded')
    def photo_uploaded(data, **kwargs):
        print(f"Customer {data['customer_id']} has uploaded an image to our service,
                and it was published at {kwargs['published_at'}.")


.. _consuming:

Consuming
_________

Once the sub is implemented, we can start our worker which will register the subscriber with Google Cloud
and will begin to pull the messages from the topic.

.. code:: python

    # worker.py

    from time import sleep
    from rele import Worker

    from settings import config
    from subs import photo_uploaded

    if __name__ == '__main__':
        worker = Worker(
            [photo_uploaded],
            config.gc_project_id,
            config.credentials,
            config.ack_deadline,
        )
        worker.run_forever()

Once the sub and worker are created, we can start our worker by running ``python worker.py``.

In another, terminal session when we run ``python publisher.py`` we should see the print readout in our subscriber.
