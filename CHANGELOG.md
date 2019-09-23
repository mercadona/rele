Changelog
=========

`0.6.0` (2019-09-21)
* BREAKING: Remove drf as a dependency (#91)
* Add message as a parameter for middleware hooks (#99)
* Check setting.CONN_MAX_AGE and warn when not 0 (#97)
* More documentation

`0.5.0` (2019-08-08)
* `python manage.py showsubscriptions` command
* Configurable ENCODER setting
* Move DEFAULT_ACK_DEADLINE to the RELE config
* More documentation

`0.4.1` (2019-06-18)
* Ability to install app only with rele
* Define default filter_by in settings.RELE

`0.4.0` (2019-06-17)

* Set `DEFAULT_ACK_DEADLINE` (#49)
* Filter by message attributes (#66) 
* BREAKING: All Relé settings are defined in a dict (#60)

Old structure:
```python
from google.oauth2 import service_account
RELE_GC_CREDENTIALS = service_account.Credentials.from_service_account_file(
    'rele/settings/dummy-credentials.json'
)
RELE_GC_PROJECT_ID = 'dummy-project-id'
```

New structure:
```python
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
```
* `rele.contrib.middleware` (#55)
* Prefix argument in sub decorator (#47) 
* Add timestamp to the published message (#42)
* BREAKING: Explicit publisher and subscriber configuration (#43)
* Sphinx documentation (#27, #34, #40, #41)
* Contributing guidelines (#32)

`0.3.1` (2019-06-04)

* Add prometheus metrics key to logs (#16 - #20, #22, #23)
* Fix JSON serialization when publishing (#25)

`0.3.0` (2019-05-14)

* Ability to run in emulator mode (#12)
* Add Travis-CI builds (#10)
* More friendly global publish (#11)
* Non-blocking behaviour when publishing by default (#6)

`0.2.0` (2019-05-09)

* Initial version
