from rele.middleware import BaseMiddleware


class UnrecoverableException(Exception):
    pass


class UnrecoverableMiddleWare(BaseMiddleware):
    def post_process_message_failure(self, subscription, err, start_time, message):
        if isinstance(err, UnrecoverableException):
            # TODO could add a config or seperate middleware
            # to push this to a new deadletter queue
            message.ack()
