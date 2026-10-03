import re

import pytest

from rele.retry_policy import RetryPolicy


class TestRetryPolicy:
    @pytest.mark.parametrize(
        "minimum_backoff, maximum_backoff",
        [
            (0, 0),
            (0, 1),
            (10, 1),
            (-5, -1),
            (-1, -1),
            (-5, 30),
            (1, -1),
            (-1, 0),
            (5, 0),
        ],
    )
    def test_value_error_is_raised_instantiating_with_wrong_values(
        self, minimum_backoff, maximum_backoff
    ):
        with pytest.raises(ValueError):
            RetryPolicy(minimum_backoff, maximum_backoff)

    def test_instantiates_with_valid_values(self):
        policy = RetryPolicy(5, 10)
        assert policy.minimum_backoff == 5
        assert policy.maximum_backoff == 10

    @pytest.mark.parametrize(
        "minimum_backoff, maximum_backoff",
        [
            (1, 1),
            (5, 30),
            (5, 5),
            (600, 600),
        ],
    )
    def test_stores_the_backoffs_it_was_given(self, minimum_backoff, maximum_backoff):
        policy = RetryPolicy(minimum_backoff, maximum_backoff)

        assert policy.minimum_backoff == minimum_backoff
        assert policy.maximum_backoff == maximum_backoff

    @pytest.mark.parametrize(
        "minimum_backoff, maximum_backoff, message",
        [
            (0, 10, "minimum_backoff must be greater than 0"),
            (-5, 10, "minimum_backoff must be greater than 0"),
            (10, 0, "maximum_backoff must be greater than 0"),
            (10, -5, "maximum_backoff must be greater than 0"),
            (30, 10, "minimum_backoff must not be greater than maximum_backoff."),
        ],
    )
    def test_names_the_parameter_that_is_wrong(
        self, minimum_backoff, maximum_backoff, message
    ):
        with pytest.raises(ValueError, match=re.escape(message)):
            RetryPolicy(minimum_backoff, maximum_backoff)
