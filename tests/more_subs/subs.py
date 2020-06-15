from rele import sub


@sub(topic="another-cool-topic", prefix="rele")
def another_sub_stub(data, **kwargs):
    return data["id"]
