from typing import TYPE_CHECKING, Any

from rele.middleware import BaseMiddleware

if TYPE_CHECKING:
    from rele.subscription import Subscription


class RetryableException(Exception):  # noqa: N818 -- named as a pair with UnrecoverableException
    pass


class RetryableMiddleWare(BaseMiddleware):
    def post_process_message_failure(
        self,
        subscription: "Subscription",
        err: Exception,
        start_time: float,
        message: Any,
    ) -> None:
        if isinstance(err, RetryableException):
            message.nack()
