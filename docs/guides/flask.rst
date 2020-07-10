.. _flask_integration:

Flask Integration
==================

.. note::
    This guide simply points out the differences between standalone Relé and
    the Flask integration. The basics about publishing and consuming are described
    in the :ref:`basics` section.

Setup
__________

To configure Relé, our settings may look something like:

.. code:: python

    from google.oauth2 import service_account
    RELE = {
        'GC_CREDENTIALS_PATH': 'photo_project/settings/dummy-credentials.json',
        'GC_PROJECT_ID': 'photo-imaging',
        'MIDDLEWARE': [
            'rele.contrib.LoggingMiddleware',
            'rele.contrib.FlaskMiddleware',
        ],
        'APP_NAME': 'photo-imaging',
    }

    # Later when we setup rele and flask:
    app = Flask()
    rele.config.setup(RELE, flask_app=app)

The only major difference here is that we are using the ``rele.contrib.FlaskMiddleware`` and
that we pass the Flask ``app`` instance to ``rele.config.setup`` method.

Subscribing
____________

Now that that the middleware is setup our subscriptions will automatically have
`Flask's app context <https://flask.palletsprojects.com/en/1.0.x/appcontext/>`_ pushed
when they are invoked so you will have access to the database connection pool and all
other app dependent utilities.

.. code:: python

    from models import File
    from database import db

    @sub(topic='photo-uploads')
    def handle_upload(data, **kwargs):
        new_file = File(data)
        db.session.add(new_file)
        db.session.commit()
