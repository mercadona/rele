from rele import sub


@sub(topic="cool-topic-for-subscription-from-pypi-package", prefix="rele")
def sub_from_sample_pypi_package(data, **kwargs):
    return data["id"]
