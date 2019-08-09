Basic Usage
===========


Creating a Simple Sub
_____________________

In order to get started using Relé, we must have a PubSub topic to publish to.
Via the Google Cloud Console we create one, named ``photo-upload``.

Once the topic is created and our Django application has the proper configuration defined
in :doc:`settings.RELE <../api/settings>`, we can start publishing to that topic from any service.


.. code:: python

    import rele

    data = {'google_bucket_location': '/google-bucket/photos/123.jpg'}

    rele.publish(topic='photo-uploaded', data=data)

To publish we simple pass in the topic to which we want our data to publish too, followed by
a valid json serializable Python object.

.. note:: If you want to publish other types of objects, you may configure the encoder class.

Once we can publish to a topic, we can subscribe to the topic from a worker instance.
In an app directory, we create our sub function with in our subs.py file.

.. code:: python

    from rele import sub

    @sub(topic='photo-uploaded')
    def photo_uploaded(data, **kwargs):
        print(f"Someone has uploaded an image to our service, and we stored it at
                {data['google_bucket_location'}.")

Once the sub is created, we can start our worker by running ``python manage.py runrele``.

The Relé worker process will autodiscover any properly decorated sub function in the subs.py filed and create the
subscription for us. Once the process is up and running, we can publish and consume.
