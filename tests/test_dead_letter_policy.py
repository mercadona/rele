import pytest

from rele.dead_letter_policy import DeadLetterPolicy


class TestDeadLetterPolicy:
    @pytest.mark.parametrize("max_delivery_attempts", [0, 4, 101, 150])
    def test_value_error_is_raised_instantiating_with_wrong_values(
        self, max_delivery_attempts
    ):
        with pytest.raises(
            ValueError, match="max_delivery_attempts must be between 5 and 100"
        ):
            DeadLetterPolicy("dlp-topic", max_delivery_attempts)

    @pytest.mark.parametrize("max_delivery_attempts", [5, 10, 100])
    def test_instantiates_with_valid_values(self, max_delivery_attempts):
        policy = DeadLetterPolicy("dlp-topic", max_delivery_attempts)
        assert policy.dead_letter_topic == "dlp-topic"
        assert policy.max_delivery_attempts == max_delivery_attempts
