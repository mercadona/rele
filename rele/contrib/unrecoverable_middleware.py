from typing import TYPE_CHECKING, Any

from rele.middleware import BaseMiddleware

if TYPE_CHECKING:
    from rele.subscription import Subscription


class UnrecoverableException(Exception):  # noqa: N818 -- renaming would break the public API
    pass


class UnrecoverableMiddleWare(BaseMiddleware):
    def post_process_message_failure(
        self,
        subscription: "Subscription",
        err: Exception,
        start_time: float,
        message: Any,
    ) -> None:
        if isinstance(err, UnrecoverableException):
            message.ack()
