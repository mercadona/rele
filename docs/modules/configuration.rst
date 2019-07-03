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
        'GC_CREDENTIALS': service_account.Credentials.from_service_account_file(
            'rele/settings/dummy-credentials.json'
        ),
        'GC_PROJECT_ID': 'dummy-project-id',
        'MIDDLEWARE': [
            'rele.contrib.LoggingMiddleware',
            'rele.contrib.DjangoDBMiddleware',
        ],
        'SUB_PREFIX': 'mysubprefix',
        'APP_NAME': 'myappname',
    }


``GC_CREDENTIALS``
------------------

**Required**

Valid Google Service Account credentials.

``GC_PROJECT_ID``
------------------

**Required**

Valid Google Project ID

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
