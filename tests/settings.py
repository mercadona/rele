from __future__ import unicode_literals, absolute_import

import os
from logging import config as logging_config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from google.oauth2 import service_account

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "Im-so-secret"

DEBUG = True
USE_TZ = True

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "rele",
]

SITE_ID = 1

MIDDLEWARE_CLASSES = ()

# Google Cloud
RELE_GC_PROJECT_ID = 'SOME-PROJECT-ID'
RELE_GC_CREDENTIALS = service_account.Credentials.from_service_account_file(
    f'{BASE_DIR}/tests/dummy-pub-sub-credentials.json'
)
RELE_SUB_PREFIX = 'rele'

RELE_MIDDLEWARE = [
    'rele.contrib.LoggingMiddleware',
    'rele.contrib.DjangoDBMiddleware',
]

logging_config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console'],
        },
    },
})
