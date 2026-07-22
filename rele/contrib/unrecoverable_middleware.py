from rele.middleware import BaseMiddleware


class UnrecoverableException(Exception):  # noqa: N818 -- renaming would break the public API
    pass


class UnrecoverableMiddleWare(BaseMiddleware):
    def post_process_message_failure(self, subscription, err, start_time, message):
        if isinstance(err, UnrecoverableException):
            message.ack()
