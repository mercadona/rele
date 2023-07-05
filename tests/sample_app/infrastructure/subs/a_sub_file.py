from rele import sub


@sub(topic="sub-inside-infra-module", prefix="rele")
def sub_inside_infra_module(data, **kwargs):
    return data["id"]
