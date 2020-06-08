import json
import os
from unittest.mock import patch

import pytest

from rele import sub
from rele.config import Config, load_subscriptions_from_paths


@sub(topic="test-topic", prefix="rele")
def sub_stub(data, **_kwargs):
    return data


class TestLoadSubscriptions:
    @pytest.fixture
    def subscriptions(self):
        return load_subscriptions_from_paths(
            ["tests.test_config"],
            sub_prefix="test",
            filter_by=lambda attrs: attrs.get("lang") == "en",
        )

    def test_load_subscriptions_in_a_module(self, subscriptions):
        assert len(subscriptions) == 1

    def test_filter_by_applied_to_subscription_returns_true(self, subscriptions):

        assert subscriptions[-1].filter_by({"lang": "en"}) is True

    def test_filter_by_applied_to_subscription_returns_false(self, subscriptions):

        assert subscriptions[0].filter_by({"lang": "es"}) is False


class TestConfig:
    def test_parses_all_keys(self, project_id, credentials, custom_encoder):
        settings = {
            "APP_NAME": "rele",
            "SUB_PREFIX": "rele",
            "GC_PROJECT_ID": project_id,
            "GC_CREDENTIALS": credentials,
            "MIDDLEWARE": ["rele.contrib.DjangoDBMiddleware"],
            "ENCODER": custom_encoder,
        }

        config = Config(settings)

        assert config.app_name == "rele"
        assert config.sub_prefix == "rele"
        assert config.gc_project_id == project_id
        assert config.credentials == credentials
        assert config.middleware == ["rele.contrib.DjangoDBMiddleware"]

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": ""})
    def test_sets_defaults(self):
        settings = {}

        config = Config(settings)

        assert config.app_name is None
        assert config.sub_prefix is None
        assert config.gc_project_id is None
        assert config.credentials is None
        assert config.middleware == ["rele.contrib.LoggingMiddleware"]
        assert config.encoder == json.JSONEncoder

    @patch.dict(
        os.environ,
        {
            "GOOGLE_APPLICATION_CREDENTIALS": os.path.dirname(
                os.path.realpath(__file__)
            )
            + "/dummy-pub-sub-credentials.json"
        },
    )
    def test_sets_defaults_pulled_from_env(self, monkeypatch, project_id, credentials):
        settings = {}

        config = Config(settings)

        assert config.app_name is None
        assert config.sub_prefix is None
        assert config.gc_project_id == "rele"
        assert config.credentials is not None
        assert config.middleware == ["rele.contrib.LoggingMiddleware"]
        assert config.encoder == json.JSONEncoder
