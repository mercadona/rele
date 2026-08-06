import json
import os
from unittest.mock import patch

import google
import pytest
from google.oauth2 import service_account

from rele import Subscription, sub
from rele.config import Config, load_subscriptions_from_paths


@sub(topic="test-topic", prefix="rele")
def sub_stub(data, **kwargs):
    return data["id"]


@sub(topic="another-cool-topic", prefix="rele")
def another_sub_stub(data, **kwargs):
    return data["id"]


@sub(
    topic="own-filter-topic",
    prefix="rele",
    filter_by=lambda attrs: attrs.get("lang") == "es",
)
def own_filter_sub_stub(data, **kwargs):
    return data["id"]


class CustomJSONEncoder(json.JSONEncoder):
    pass


class TestLoadSubscriptions:
    @pytest.fixture
    def subscriptions(self):
        return load_subscriptions_from_paths(
            ["tests.test_config"],
            sub_prefix="test",
            filter_by=[lambda args: args.get("lang") == "en"],
        )

    def test_load_subscriptions_in_a_module(self, subscriptions):
        assert len(subscriptions) == 3
        func_sub = subscriptions[-1]
        assert isinstance(func_sub, Subscription)
        assert func_sub.name == "rele-test-topic"
        assert func_sub({"id": 4}, lang="en") == 4

    def test_applies_filter_when_filter_by_is_a_single_callable(self):
        subscriptions = load_subscriptions_from_paths(
            ["tests.subs"],
            sub_prefix="test",
            filter_by=lambda attrs: attrs.get("lang") == "en",
        )

        assert subscriptions[0]({"id": 4}, lang="en") == 4
        assert subscriptions[0]({"id": 4}, lang="es") is None

    def test_loads_subscriptions_when_they_are_class_based(self):
        subscriptions = load_subscriptions_from_paths(
            ["tests.subs"],
            sub_prefix="test",
            filter_by=[lambda attrs: attrs.get("lang") == "en"],
        )

        assert len(subscriptions) == 2
        klass_sub = subscriptions[0]
        assert isinstance(klass_sub, Subscription)
        assert klass_sub.name == "test-alternative-cool-topic"
        assert klass_sub({"id": 4}, lang="en") == 4

    def test_avoid_duplicates_when_importing_same_sub_instance_from_different_places(
        self,
    ):
        subscriptions = load_subscriptions_from_paths(
            [
                "tests.sample_app.subs",
                "tests.sample_app.another_folder.subs",
                "tests.sample_app.infrastructure.subs",
            ],
            sub_prefix="sub",
            filter_by=[lambda attrs: attrs.get("lang") == "en"],
        )

        assert len(subscriptions) == 2
        subs_names = [subscription.name for subscription in subscriptions]
        assert "rele-sub-inside-another-module" in subs_names
        assert "rele-sub-inside-infra-module" in subs_names

    def test_keeps_own_filter_when_a_global_filter_by_is_given(self, subscriptions):
        own_filter_sub = next(
            subscription
            for subscription in subscriptions
            if subscription.name == "rele-own-filter-topic"
        )

        assert own_filter_sub({"id": 4}, lang="es") == 4
        assert own_filter_sub({"id": 4}, lang="en") is None

    def test_keeps_loading_module_subs_after_an_already_registered_instance(self):
        subscriptions = load_subscriptions_from_paths(
            [
                "tests.sample_app.another_folder.subs",
                "tests.sample_app.subs",
            ],
            sub_prefix="sub",
            filter_by=[lambda attrs: attrs.get("lang") == "en"],
        )

        subs_names = [subscription.name for subscription in subscriptions]
        assert subs_names == [
            "rele-sub-inside-another-module",
            "rele-sub-inside-infra-module",
        ]

    def test_raises_error_when_subscription_is_duplicated(self):
        with pytest.raises(RuntimeError) as excinfo:
            load_subscriptions_from_paths(["tests.test_config", "tests.more_subs.subs"])

        assert (
            str(excinfo.value)
            == "Duplicate subscription name found: rele-another-cool-topic. Subs "
            "tests.more_subs.subs.another_sub_stub and tests.test_config.another_sub_stub collide."
        )

    def test_returns_sub_value_when_filtered_value_applied(self, subscriptions):
        assert subscriptions[-1]({"id": 4}, lang="en") == 4

    def test_returns_none_when_filtered_value_does_not_apply(self, subscriptions):
        assert subscriptions[0]({"id": 4}, lang="es") is None


class TestConfig:
    def test_parses_all_keys(self, project_id):
        def filter_by_english(attrs):
            return attrs.get("lang") == "en"

        settings = {
            "APP_NAME": "rele",
            "SUB_PREFIX": "rele",
            "GC_CREDENTIALS_PATH": "tests/dummy-pub-sub-credentials.json",
            "MIDDLEWARE": ["rele.contrib.DjangoDBMiddleware"],
            "ENCODER_PATH": "tests.test_config.CustomJSONEncoder",
            "PUBLISHER_BLOCKING": True,
            "PUBLISHER_TIMEOUT": 99.5,
            "THREADS_PER_SUBSCRIPTION": 7,
            "ACK_DEADLINE": 120,
            "FILTER_SUBS_BY": [filter_by_english],
        }

        config = Config(settings)

        assert config.app_name == "rele"
        assert config.sub_prefix == "rele"
        assert config.gc_project_id == project_id
        assert isinstance(config.credentials, service_account.Credentials)
        assert config.middleware == ["rele.contrib.DjangoDBMiddleware"]
        assert config.encoder is CustomJSONEncoder
        assert config.publisher_blocking is True
        assert config.publisher_timeout == 99.5
        assert config.threads_per_subscription == 7
        assert config.ack_deadline == 120
        assert config.filter_by == [filter_by_english]

    def test_uses_project_id_from_settings_when_given(self):
        settings = {
            "GC_PROJECT_ID": "settings-project",
            "GC_CREDENTIALS_PATH": "tests/dummy-pub-sub-credentials.json",
        }

        config = Config(settings)

        assert config.gc_project_id == "settings-project"
        assert config.credentials.project_id == "rele-test"
        assert config.gc_project_id == "settings-project"

    def test_inits_service_account_creds_when_credential_path_given(self, project_id):
        settings = {
            "GC_CREDENTIALS_PATH": "tests/dummy-pub-sub-credentials.json",
        }

        config = Config(settings)

        assert config.gc_project_id == project_id
        assert isinstance(config.credentials, google.oauth2.service_account.Credentials)
        assert config.credentials.project_id == "rele-test"

    def test_uses_project_id_from_creds_when_no_project_id_given(self):
        settings = {
            "GC_CREDENTIALS_PATH": "tests/dummy-pub-sub-credentials.json",
        }

        config = Config(settings)

        assert isinstance(config.credentials, google.oauth2.service_account.Credentials)
        assert config.credentials.project_id == "rele-test"
        assert config.gc_project_id == "rele-test"

    @patch("rele.config.get_google_defaults", return_value=(None, None))
    def test_sets_defaults(self, _mock_google_defaults):
        settings = {}

        config = Config(settings)

        assert config.app_name is None
        assert config.sub_prefix is None
        assert config.gc_project_id is None
        assert config.credentials is None
        assert config.middleware == ["rele.contrib.LoggingMiddleware"]
        assert config.encoder == json.JSONEncoder
        assert config.publisher_blocking is False

    def test_returns_no_project_id_when_default_creds_have_none(self):
        class UserAdcCredentials:
            """What google.auth.default() returns under user ADC."""

            token = "a-token"

        with patch(
            "rele.config.get_google_defaults",
            return_value=(UserAdcCredentials(), None),
        ):
            config = Config({})

            assert config.gc_project_id is None

    @patch.dict(
        os.environ,
        {
            "GOOGLE_APPLICATION_CREDENTIALS": os.path.dirname(
                os.path.realpath(__file__)
            )
            + "/dummy-pub-sub-credentials.json"
        },
    )
    def test_sets_defaults_pulled_from_env(self, monkeypatch, project_id):
        settings = {}

        config = Config(settings)

        assert config.app_name is None
        assert config.sub_prefix is None
        assert config.gc_project_id == "rele-test"
        assert isinstance(config.credentials, google.oauth2.service_account.Credentials)
        assert config.middleware == ["rele.contrib.LoggingMiddleware"]
        assert config.encoder == json.JSONEncoder
        assert config.publisher_blocking is False
