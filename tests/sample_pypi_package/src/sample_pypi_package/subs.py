from rele import sub


@sub(topic="topic-from-third-party-package", prefix="rele")
def sub_from_third_party_package(data, **kwargs):
    return data["id"]
