import pytest
from rele.config import load_subscriptions_from_paths
from rele import sub


@sub(topic='test-topic', prefix='rele')
def sub_stub(data, **_kwargs):
    return data


class TestLoadSubscriptions:
    @pytest.fixture
    def subscriptions(self):
        return load_subscriptions_from_paths(
            ['tests.test_config'],
            sub_prefix='test',
            filter_by=lambda **attrs: attrs.get('lang') == 'en')

    def test_load_subscriptions_in_a_module(self, subscriptions):
        assert len(subscriptions) == 1

    def test_filter_by_applied_to_subscription_returns_true(
            self, subscriptions):

        assert subscriptions[-1].filter_by(**{'lang': 'en'}) is True

    def test_filter_by_applied_to_subscription_returns_false(
            self, subscriptions):

        assert subscriptions[0].filter_by(**{'lang': 'es'}) is False
