<p align="center">
    <img src="docs/_static/rele_logo.png" align="center" height="200">
</p>

<p align="center">
    <strong>
        Relé makes integration with Google PubSub straightforward and easy.
    </strong>
</p>

<p align="center">
    <a href="https://travis-ci.org/mercadona/rele">
        <img src="https://travis-ci.org/mercadona/rele.svg?branch=master"
             alt="Build Status">
    </a>
    <a href="https://mercadonarele.readthedocs.io/en/latest/?badge=latest">
        <img src="https://readthedocs.org/projects/mercadonarele/badge/?version=latest"
             alt="Read the Docs">
    </a>
    <a href="https://codecov.io/gh/mercadona/rele">
        <img src="https://codecov.io/gh/mercadona/rele/branch/master/graph/badge.svg"
             alt="Code Coverage">
    </a>
    <a href="https://pypi.org/project/rele/">
        <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/rele.svg">
    </a>
    <a href="https://pypi.org/project/rele/">
        <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/rele">
    </a>
</p>


## Motivation and Features

The [Publish-Subscribe pattern](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern) 
and specifically the Google Cloud [Pub/Sub library](https://pypi.org/project/google-cloud-pubsub/) 
are very powerful tools but you can easily cut your fingers on it. Relé makes integration 
seamless by providing Publisher, Subscriber and Worker classes with the following features:

* Powerful Publishing API
* Highly Scalable Worker
* Intuitive Subscription Management
* Easily Extensible Middleware
* Ready to go Django/Flask integration
* CLI
* And much more!

## What it looks like

```python
# Publish to the topic
import rele

rele.publish(topic='photo-uploaded', data={'customer_id': 123})

# Subscribe to the Pub/Sub topic
from rele import sub

@sub(topic='photo-uploaded')
def photo_uploaded(data, **kwargs):
    print(f"Customer {data['customer_id']} has uploaded an image")
```

## What's in the name

"Relé" is Spanish for *relay*, a technology that 
[has played a key role](https://technicshistory.wordpress.com/2017/01/29/the-relay/) in 
history in the evolution of communication and electrical technology, including the telegraph, 
telephone, electricity transmission, and transistors.

## Install

Relé supports Python 3.6+ and installing via ``pip``

`pip install rele`

or with Django integration

`pip install rele[django]`

or with Flask integration

`pip install rele[flask]`

## Quickstart

[Please see our documentation to get started.](https://mercadonarele.readthedocs.io/en/latest/guides/basics.html) 

You can also read more about it [here](https://medium.com/mercadona-tech/announcing-rel%C3%A9-c2d0540af3b9)

----

## Running Tests

Does the code actually work?

      make test
