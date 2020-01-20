from rele.middleware import BaseMiddleware


class UnrecoverableException(Exception):
    pass


class UnrecoverableMiddleWare(BaseMiddleware):
    def post_process_message_failure(self, subscription, err, start_time, message):
        if isinstance(err, UnrecoverableException):
            message.ack()
