from dataclasses import dataclass


@dataclass
class DeadLetterPolicy:
    dead_letter_topic: str
    max_delivery_attempts: int

    def __init__(self, dead_letter_topic: str, max_delivery_attempts: int) -> None:
        self._guard_against_wrong_parameters(max_delivery_attempts)

        self.dead_letter_topic = dead_letter_topic
        self.max_delivery_attempts = max_delivery_attempts

    def _guard_against_wrong_parameters(self, max_delivery_attempts: int) -> None:
        if max_delivery_attempts < 5 or max_delivery_attempts > 100:
            raise ValueError("max_delivery_attempts must be between 5 and 100")
