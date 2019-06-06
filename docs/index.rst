.. Rele documentation master file, created by
   sphinx-quickstart on Wed Jun  5 14:19:08 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Rele's documentation!
================================

Release v\ |version|. (`Installation <https://github.com/mercadona/rele>`_)

.. image:: https://travis-ci.org/mercadona/rele.svg?branch=master
    :target: https://travis-ci.org/mercadona/rele

.. image:: https://img.shields.io/badge/license-Apache%202-blue.svg
    :target: https://github.com/mercadona/rele/blob/master/LICENSE

**Relé** makes integration with Google PubSub easier and is ready to integrate seamlessly into any Django project.

Motivation and Features
_______________________
The Publish-Subscribe pattern and specifically the Google Cloud PubSub library are very powerful tools but you can easily cut your fingers on it. Relé makes integration seamless by providing Publisher, Subscriber and Worker classes with the following features:

    * A **publish** function
    * A sub decorator to declare subscribers
    * **Publisher** and **Subscription** classes
    * A **Worker** class
    * A **python manage.py runrele** management command

Modules
_______

.. toctree::
   :maxdepth: 2

   subscription

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
