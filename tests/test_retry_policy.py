import pytest

from rele.retry_policy import RetryPolicy


class TestRetryPolicy:
    @pytest.mark.parametrize(
        "minimum_backoff, maximum_backoff",
        [
            (0, 0),
            (0, 1),
            (10, 1),
        ],
    )
    def test_value_error_is_raised_instantiating_with_wrong_values(
        self, minimum_backoff, maximum_backoff
    ):
        with pytest.raises(ValueError):
            RetryPolicy(minimum_backoff, maximum_backoff)
