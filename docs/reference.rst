API Reference
=============

.. module:: rele

.. _ client

Clients
-------

.. autoclass:: rele.client.Publisher
   :members:


.. _ publish

.. autoclass:: rele.client.Subscriber
   :members:


.. _ subscriber

Publish
-------

.. automodule:: rele.publishing
   :members:


.. _ subscription

Subscription
------------

.. automodule:: rele.subscription
   :members:


.. _ worker

Worker
------

.. automodule:: rele.worker
   :members:


.. _ middleware

Middleware
----------

Relé middleware's provide additional functionality to default behavior. Simply subclass
``BaseMiddleware`` and declare the hooks you wish to use.

Base Middleware
---------------

.. autoclass:: rele.middleware.BaseMiddleware
   :members:

Logging Middleware
------------------

.. automodule:: rele.contrib.logging_middleware
   :members:

Django Middleware
-----------------

.. automodule:: rele.contrib.django_db_middleware
   :members:
