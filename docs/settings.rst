.. _settings:

========
Settings
========

.. contents::
    :local:
    :depth: 1


``RELE``
--------

Default: ``{}`` (Empty dictionary)

A dictionary mapping all Relé configuration settings to values defined
in your Django project's ``settings.py``.
Example::

    RELE = {
        'GC_CREDENTIALS_PATH': 'rele/settings/dummy-credentials.json',
        'MIDDLEWARE': [
            'rele.contrib.LoggingMiddleware',
            'rele.contrib.DjangoDBMiddleware',
        ],
        'SUB_PREFIX': 'mysubprefix',
        'APP_NAME': 'myappname',
        'ENCODER_PATH': 'rest_framework.utils.encoders.JSONEncoder',
        'ACK_DEADLINE': 120,
        'PUBLISHER_TIMEOUT': 3.0,
        'FILTER_SUBS_BY': boolean_function,
        'DEFAULT_RETRY_POLICY': {
            'minimum_backoff': 10,
            'maximum_backoff': 60,
        },
        'DEAD_LETTER_TOPIC_ID': 'dead-letter-topic',
        'MAX_DELIVERY_ATTEMPTS': 5,
    }

``GC_PROJECT_ID``
------------------

**Optional**

GCP project id to use. If this is not provided then it is inferred via either
service account's project id or quota project id if using Application Default Credentials (ADC)


``GC_CREDENTIALS_PATH``
-----------------------

**Optional**

Path to service account json file with access to PubSub


.. _settings_project_id:

``MIDDLEWARE``
------------------

**Optional**

Default: ``['rele.contrib.LoggingMiddleware']``

List of the middleware modules that will be included in the project. The order
of execution follows FIFO.

It is strongly recommended that for Django integration, you add::

    [
        'rele.contrib.LoggingMiddleware',
        'rele.contrib.DjangoDBMiddleware',
    ]

The DjangoDBMiddleware will take care of opening and closing connections to the db before
and after your callbacks are executed. If this is left out, it is highly probable that
your database will run out of connections in your connection pool.

The LoggingMiddleware will take care of logging subscription information before and after the callback is executed.
The subscription message is only logged when an exception was raised while processing it.
If you would like to log this message in every case, you should create a middleware of your own.


``SUB_PREFIX``
------------------

**Optional**

A prefix to all your subs that can be declared globally.

For instance, if you have two projects listening to one topic, you may want to add a
prefix so that there can be two distinct subscribers to that one topic.


``APP_NAME``
------------------

**Optional**

The application name.

This should be unique to all the services running in the application ecosystem. It is used by
the LoggingMiddleware and Prometheus integration.

.. _settings_encoder_path:

``ENCODER_PATH``
------------------

**Optional**

Default: `rest_framework.utils.encoders.JSONEncoder <https://github.com/encode/django-rest-framework/blob/master/rest_framework/utils/encoders.py#L17>`_

`Encoder class path <https://docs.python.org/3/library/json.html#json.JSONEncoder>`_ to use for
serializing your Python data structure to a json object when publishing.

.. note:: The default encoder class is subject to change in an upcoming release.
    It is advised that you use this setting explicitly.

``ACK_DEADLINE``
------------------

**Optional**

Ack deadline for all subscribers in seconds.

.. seealso:: The `Google Pub/Sub documentation <https://cloud.google.com/pubsub/docs/subscriber>`_
    which states that *The subscriber has a configurable, limited amount of time --
    known as the ackDeadline -- to acknowledge the outstanding message. Once the deadline
    passes, the message is no longer considered outstanding, and Cloud Pub/Sub will attempt
    to redeliver the message.*

.. _settings_publisher_timeout:

``PUBLISHER_TIMEOUT``
---------------------

**Optional**

Default: 3.0 seconds

Timeout that the publishing result will wait on the future to publish successfully while blocking.

`See Google PubSub documentation for more info
<https://googleapis.dev/python/pubsub/1.1.0/publisher/api/futures.html?highlight=result#google.cloud.pubsub_v1.publisher.futures.Future.result>`_

``THREADS_PER_SUBSCRIPTION``
----------------------------

**Optional**

Default: 2

Number of threads that will be consumed for each subscription.
Default behavior of the Google Cloud PubSub library is to use 10 threads per subscription.
We thought this was too much for a default setting and have taken the liberty of
reducing the thread count to 2. If you would like to maintain the default Google PubSub
library behavior, please set this value to 10.

``FILTER_SUBS_BY``
----------------------------

**Optional**

Boolean function that applies a global filter on all subscriptions.
For more information, please see `Filtering Messages section <https://mercadonarele.readthedocs.io/en/latest/guides/filters.html#global-filter>`.


``DEFAULT_RETRY_POLICY``
----------------------------

**Optional**

Dictionary with two keys: `minimum_backoff` and `maximum_backoff`, that specifies how Pub/Sub retries message delivery for all the subscriptions.

    If not set, the default retry policy is applied. This generally implies that messages will be retried as soon as possible for healthy subscribers. RetryPolicy will be triggered on NACKs or acknowledgement deadline exceeded events for a given message.


``DEAD_LETTER_TOPIC_ID``
----------------------------

**Optional**

String defines the name of the topic to which dead letter messages should be published.


``MAX_DELIVERY_ATTEMPTS``
----------------------------

**Optional**

Default: 5 times

Integer defines the maximum number of delivery attempts for any message.
Both `DEAD_LETTER_TOPIC_ID` and `MAX_DELIVERY_ATTEMPTS` define the `DeadLetterPolicy`.
It is essential to note that the `MAX_DELIVERY_ATTEMPTS` is ignored when the `DEAD_LETTER_TOPIC_ID` is not set.
