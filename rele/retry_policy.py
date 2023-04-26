from dataclasses import dataclass


@dataclass
class RetryPolicy:
    """A RetryPolicy object encapsulates the validation rules.

    Defines retry policy settings and ensures the values are correct.
    If provided values are wrong, a ValidationError is raised.

    :param minimum_backoff: int Accepts values greater than 0
    :param maximum_backoff: int Accepts values greater than minimum_backoff.
    """

    minimum_backoff: int
    maximum_backoff: int

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
