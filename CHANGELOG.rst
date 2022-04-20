Changelog
=========

1.5.0 (2022-04-20)
-------------------
* [Added] Add filter expressions to subscriptions. (#207)

1.4.1 (2022-04-19)
-------------------
* [Modified] Fixed bug in the post-publish-failure VerboseLoggingMiddleware hook. (#220)

1.4.0 (2022-04-13)
-------------------
* [Added] Added a VerboseLoggingMiddleware that does not truncate mesage payload. (#218)

1.3.0 (2022-04-04)
-------------------
* GC Project Id & Windows support (#215)

1.2.0 (2021-12-10)
-------------------
* [CHANGED] TimeotError from publisher (#212)
* Added filter_subs_by setting in documentation (#208)
* Automatic topic creation (#206)
* Log post publish success (#204)

1.1.1 (2021-6-28)
-------------------
* Do not define default_app_config, it's deprecated (#199)
* Do not implement deprecated middlewares in the base class (#200)

1.1.0 (2021-3-10)
-------------------
* Google Pubsub 2.0 Compat (#192)
* Add validations to the sub decorator (#189)
* Add new post_publish_hook and deprecate the old one (#190)
* Discover and load settings when publishing (#188)
* Fix #180: Raise error when the config loads a repeated subscription (#187)

1.0.0 (2020-9-25)
-------------------
* BREAKING: Remove GC_PROJECT_ID (#183)

0.14.0 (2020-8-5)
-------------------
* BREAKING: Remove GC_CREDENTIALS (#174)
* Add changelog to the docs site (#179)
* Catch TimeoutError and run post_publish_failure when blocking (#172)
* Deprecate GC_PROJECT_ID setting (#178)

0.13.0 (2020-7-9)
-------------------
* Add documentation for class based subscriptions (#169)
* Deprecate GC_CREDENTIALS setting (#173)
* GC_CREDENTIALS_PATH setting option (#170)

0.13.dev0 (2020-6-16)
---------------------
* Traverse all packages to autodiscover all subs.py modules (#167)
* Auto-discovery of class based subscriptions (#168)

0.12.0 (2020-6-12)
-------------------
* Added ``--settings`` path option in CLI (#166)
* Added isort linting (#164)

0.11.0 (2020-6-4)
-------------------
* CLI feature (#160)
* Documentation Enhancements (#158, #155, #162)
* Testing Improvements (#154, #157)

0.10.0 (2020-2-4)
-------------------
* Adjust default THREADS_PER_SUBSCRIPTION (#152)
* Add unrecoverable_middleware (#150)
* Allow multiple filters (#148)
* Configure timeout from .publish() (#143)
* Dont crash when subscription topic does not exist (#142)

0.9.1 (2020-1-2)
-------------------
* Ack messages when data not json serializable (#141)
* Use ThreadScheduler instead of ThreadPoolExecutor (#145)

0.9.0 (2019-12-20)
-------------------
* Flask support via middleware (#127)
* Add message attributes to metrics log (#128)
* Specify number of threads per subscriber with Subscription ThreadPoolExecutor (#139)
* Publishing timeout while blocking (#137)
* Clean up rele.config.setup + Worker() init (#132)

0.8.1 (2019-11-25)
-------------------
* Fix runrele command

0.8.0 (2019-11-22)
-------------------
* Worker run method (#118)
* Add kwargs to setup method passed through to middleware (#123)
* Add missing worker middleware hooks (#121)
* Add 3.8 support
* More Documentation

0.7.0 (2019-10-21)
-------------------
* BREAKING: Remove Django as a dependency (#95)
* More documentation

0.6.0 (2019-09-21)
-------------------
* BREAKING: Remove drf as a dependency (#91)
* Add message as a parameter for middleware hooks (#99)
* Check setting.CONN_MAX_AGE and warn when not 0 (#97)
* More documentation

0.5.0 (2019-08-08)
-------------------
* ``python manage.py showsubscriptions`` command
* Configurable ENCODER setting
* Move DEFAULT_ACK_DEADLINE to the RELE config
* More documentation

0.4.1 (2019-06-18)
-------------------
* Ability to install app only with rele
* Define default filter_by in settings.RELE

0.4.0 (2019-06-17)
-------------------

* Set ``DEFAULT_ACK_DEADLINE`` (#49)
* Filter by message attributes (#66)
* BREAKING: All Relé settings are defined in a dict (#60)

Old structure:

.. code:: python

    from google.oauth2 import service_account
    RELE_GC_CREDENTIALS = service_account.Credentials.from_service_account_file(
        'rele/settings/dummy-credentials.json'
    )
    RELE_GC_PROJECT_ID = 'dummy-project-id'

New structure:

.. code:: python

    from google.oauth2 import service_account
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

* ``rele.contrib.middleware`` (#55)
* Prefix argument in sub decorator (#47)
* Add timestamp to the published message (#42)
* BREAKING: Explicit publisher and subscriber configuration (#43)
* Sphinx documentation (#27, #34, #40, #41)
* Contributing guidelines (#32)

0.3.1 (2019-06-04)
-------------------

* Add prometheus metrics key to logs (#16 - #20, #22, #23)
* Fix JSON serialization when publishing (#25)

0.3.0 (2019-05-14)
-------------------

* Ability to run in emulator mode (#12)
* Add Travis-CI builds (#10)
* More friendly global publish (#11)
* Non-blocking behaviour when publishing by default (#6)

0.2.0 (2019-05-09)
-------------------

* Initial version
