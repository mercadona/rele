from unittest.mock import patch

import pytest
from django.core.management import call_command

from rele.subscription import sub


@sub(topic="some-cool-topic", prefix="rele")
def sub_stub(data, **kwargs):
    return data["id"]


@sub(topic="some-fancy-topic")
def sub_fancy_stub(data, **kwargs):
    return data["id"]


@sub(topic="published-time-type")
def sub_published_time_type(data, **kwargs):
    return f'{type(kwargs["published_at"])}'


def landscape_filter(**kwargs):
    return kwargs.get("type") == "landscape"


@sub(topic="photo-updated", filter_by=landscape_filter)
def sub_process_landscape_photos(data, **kwargs):
    return f'Received a photo of type {kwargs.get("type")}'


@pytest.fixture()
def mock_discover_subs():
    affected_path = (
        "rele.management.commands.showsubscriptions" ".discover_subs_modules"
    )
    with patch(affected_path, return_value=[__name__]) as mock:
        yield mock


class TestShowSubscriptions:
    def test_prints_table_when_called(self, capfd, mock_discover_subs):
        call_command("showsubscriptions")

        mock_discover_subs.assert_called_once()
        captured = capfd.readouterr()
        assert (
            captured.out
            == """Topic                Subscriber(s)         Sub
-------------------  --------------------  ----------------------------
photo-updated        photo-updated         sub_process_landscape_photos
published-time-type  published-time-type   sub_published_time_type
some-cool-topic      rele-some-cool-topic  sub_stub
some-fancy-topic     some-fancy-topic      sub_fancy_stub
"""
        )
