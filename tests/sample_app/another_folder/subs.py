from rele import sub


@sub(topic="sub-inside-another-module", prefix="rele")
def sub_inside_another_module(data, **kwargs):
    return data["id"]
