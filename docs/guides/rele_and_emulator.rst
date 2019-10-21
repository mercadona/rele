Using the Google Cloud Pub/Sub emulator
=======================================

It can be helpful to be able run the emulator in our development environment.
To be able to do that we can follow the steps below:

1) Run the Google Cloud Pub/Sub emulator in the cloud-sdk container and map the port 8085.

.. code:: bash

    docker pull google/cloud-sdk # Pull container
    docker run -it --rm -p "8085:8085" google/cloud-sdk gcloud beta emulators pubsub start --host-port=0.0.0.0:8085


2) Export PUBSUB_EMULATOR_HOST environment variable to specify the emulator host.

    In case you don't want to set this variable, it will be necessary to have pub/sub crendentials.

.. code:: bash

    export PUBSUB_EMULATOR_HOST=localhost:8085


3) Set rele settings in the Django project.

.. code:: python

    # my_django_project/settings.py

    RELE = {
        'APP_NAME': 'my-awesome-app',
        'SUB_PREFIX': 'test',
        'GC_PROJECT_ID': 'my-awesome-project',
        'GC_CREDENTIALS': 'my-credentials',
        'MIDDLEWARE': [
            'rele.contrib.LoggingMiddleware',
            'rele.contrib.DjangoDBMiddleware',
        ],
    }


In case it's necessary to create a topic manually we can add it using the django shell.

.. code:: bash

    python manage.py shell

.. code:: python

    from django.conf import settings
    from google.cloud import pubsub_v1

    publisher_client = pubsub_v1.PublisherClient()
    topic_path = publisher_client.topic_path(settings.RELE.get('GC_PROJECT_ID'), 'topic_name')
    publisher_client.create_topic(topic_path)
