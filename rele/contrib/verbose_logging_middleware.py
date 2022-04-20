import json

from rele.contrib.logging_middleware import LoggingMiddleware


class VerboseLoggingMiddleware(LoggingMiddleware):
    def post_process_message_failure(
        self, subscription, exception, start_time, message
    ):
        super().post_process_message_failure(
            subscription, exception, start_time, _VerboseMessage(message)
        )


class _VerboseMessage:
    def __init__(self, message):
        self._message = message
        self.attributes = message.attributes

    def __repr__(self):
        _MESSAGE_REPR = """\
Message {{
  data: {!r}
  ordering_key: {!r}
  attributes: {}
}}"""

        data = self._message._message.data
        attrs = self._message_attrs_repr()
        ordering_key = str(self._message.ordering_key)

        return _MESSAGE_REPR.format(data, ordering_key, attrs)

    def _message_attrs_repr(self):
        message_attrs = json.dumps(
            dict(self.attributes), indent=2, separators=(",", ": "), sort_keys=True
        )

        indented = []
        for line in message_attrs.split("\n"):
            indented.append("  " + line)

        message_attrs = "\n".join(indented)
        message_attrs = message_attrs.lstrip()

        return message_attrs
