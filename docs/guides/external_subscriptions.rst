.. _external_subscriptions:

Managing subscriptions outside Relé
===================================

By default, when the worker starts it creates every subscription it consumes
and, if the topic of a subscription does not exist, the topic too. If the
subscription already exists, the worker updates it with the configuration
declared in Relé.

If you provision Pub/Sub with infrastructure-as-code (Terraform, Pulumi,
Deployment Manager...) you may want the worker to only consume, and to run
with a service account that cannot create or modify Pub/Sub resources. Set
:ref:`settings_manage_subscriptions` to ``False``:

.. code:: python

    RELE = {
        # ...
        'MANAGE_SUBSCRIPTIONS': False,
    }

With this setting the worker skips the create/update step entirely: it
registers the callbacks and starts consuming, nothing else. On startup it logs
one ``INFO`` line saying that subscription management is disabled.

The setting is global: it applies to every subscription of the worker.

Required permissions
____________________

The service account running the worker then needs:

* ``roles/pubsub.subscriber`` on each subscription it consumes.
* ``roles/pubsub.publisher`` on the topics it publishes to, if the project
  also publishes with Relé.

No project-wide ``roles/pubsub.editor`` is needed.

Subscriptions must exist beforehand
___________________________________

Each subscription must exist before the worker starts, with the exact name
Relé computes for it (``prefix-topic-suffix``; see ``SUB_PREFIX`` and the
``prefix``/``suffix`` arguments of ``@sub``). Run
``python manage.py showsubscriptions`` in Django projects to list them.

If a subscription does not exist, the error raised by the Pub/Sub client when
consuming it surfaces as usual; Relé does not swallow it.

Configuration that is no longer applied
_______________________________________

.. warning:: When ``MANAGE_SUBSCRIPTIONS`` is ``False``, the following Relé
    configuration is **not** applied to the subscriptions or topics, because
    Relé never writes to them. Configure it in your infrastructure code instead:

    * ``DEFAULT_RETRY_POLICY`` and the ``retry_policy`` argument of ``@sub``.
    * ``backend_filter_by`` (the Pub/Sub subscription filter). Local filters
      (``filter_by`` and ``FILTER_SUBS_BY``) still run in the worker.
    * ``ACK_DEADLINE``, as the subscription's ack deadline.
    * ``GC_STORAGE_REGION``, as the message storage policy of auto-created topics.
    * Any future subscription-level policy configured in Relé (for example a
      dead-letter policy).
