from __future__ import absolute_import, unicode_literals

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

DATABASES = {"default": {"CONN_MAX_AGE": 0}}

RELE = {
    "APP_NAME": "test-rele",
    "GC_PROJECT_ID": "SOME-PROJECT-ID",
    "GC_CREDENTIALS_PATH": f"{BASE_DIR}/tests/dummy-pub-sub-credentials.json",
    "SUB_PREFIX": "rele",
    "MIDDLEWARE": [
        "rele.contrib.LoggingMiddleware",
        "rele.contrib.DjangoDBMiddleware",
    ],
}

logging_config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "loggers": {"": {"level": "INFO", "handlers": ["console"]}},
    }
)
