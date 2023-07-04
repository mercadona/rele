from rele import sub


@sub(topic="sub-inside-a-module", prefix="rele")
def sub_inside_a_module(data, **kwargs):
    return data["id"]
