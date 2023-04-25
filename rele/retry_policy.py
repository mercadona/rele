from dataclasses import dataclass


@dataclass
class RetryPolicy:
    minimum_backoff: None
    maximum_backoff: None

    def __init__(self, minimum_backoff, maximum_backoff):
        self._guard_against_wrong_parameters(minimum_backoff, maximum_backoff)

        self.minimum_backoff = minimum_backoff
        self.maximum_backoff = maximum_backoff

    def _guard_against_wrong_parameters(self, minimum_backoff, maximum_backoff):
        if minimum_backoff == 0:
            raise ValueError("minimum_backoff must be greater than 0")

        if maximum_backoff == 0:
            raise ValueError("maximum_backoff must be greater than 0")

        if minimum_backoff > maximum_backoff:
            raise ValueError("minimum_backoff should be less than maximum_backoff.")
