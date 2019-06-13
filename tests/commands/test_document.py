from unittest.mock import patch

from django.core.management import call_command


class TestDocument:

    @patch('rele.management.commands.document.tabulate',
           autospec=True, return_value='')
    def test_prints_table_when_called(self, mock_tabulate):
        expected_headers = ['Topic', 'Subscriber(s)', 'Sub']
        call_command('document')

        mock_tabulate.assert_called_once_with([], headers=expected_headers)
