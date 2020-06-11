from rele import sub


@sub(topic="some-cool-topic", prefix="rele")
def sub_stub(data, **kwargs):
    return data["id"]
