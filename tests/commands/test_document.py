from unittest.mock import patch

import pytest
from django.core.management import call_command

from rele.subscription import sub


@sub(topic='some-cool-topic', prefix='rele')
def sub_stub(data, **kwargs):
    return data['id']


@sub(topic='some-fancy-topic')
def sub_fancy_stub(data, **kwargs):
    return data['id']


@sub(topic='published-time-type')
def sub_published_time_type(data, **kwargs):
    return f'{type(kwargs["published_at"])}'


def landscape_filter(**kwargs):
    return kwargs.get('type') == 'landscape'


@sub(topic='photo-updated', filter_by=landscape_filter)
def sub_process_landscape_photos(data, **kwargs):
    return f'Received a photo of type {kwargs.get("type")}'


@pytest.fixture()
def mock_tabulate():
    affected_path = 'rele.management.commands.document.tabulate'
    with patch(affected_path, autospec=True, return_value='') as mock:
        yield mock


@pytest.fixture()
def mock_discover_subs():
    affected_path = 'rele.management.commands.document.discover_subs_modules'
    with patch(affected_path, return_value=[__name__]) as mock:
        yield mock


class TestDocument:

    def test_prints_table_when_called(self, mock_discover_subs, mock_tabulate):
        expected_headers = ['Topic', 'Subscriber(s)', 'Sub']
        expected_subscription_data = [
            ('photo-updated', 'photo-updated', 'sub_process_landscape_photos'),
            ('published-time-type', 'published-time-type', 'sub_published_time_type'),
            ('some-cool-topic', 'rele-some-cool-topic', 'sub_stub'),
            ('some-fancy-topic', 'some-fancy-topic', 'sub_fancy_stub'),
        ]

        call_command('document')

        mock_tabulate.assert_called_once_with(expected_subscription_data, headers=expected_headers)
        mock_discover_subs.assert_called_once()
