from rele import Subscription, sub


@sub(topic="some-cool-topic", prefix="rele")
def sub_stub(data, **kwargs):
    return data["id"]


class KlassBasedSub(Subscription):
    topic = "alternative-cool-topic"

    def __init__(self):
        self._func = self.callback_func
        super().__init__(self._func, self.topic)

    def callback_func(self, data, **kwargs):
        return data["id"]


class CustomException(Exception):
    pass


def some_other_type():
    print("Im a function")
