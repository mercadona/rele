from typing import TYPE_CHECKING, Any

from rele.middleware import BaseMiddleware

if TYPE_CHECKING:
    from rele.config import Config
    from rele.subscription import Subscription


class FlaskMiddleware(BaseMiddleware):
    def setup(self, config: "Config", **kwargs: Any) -> None:
        self.app = kwargs["flask_app"]

    def pre_process_message(self, subscription: "Subscription", message: Any) -> None:
        self.ctx = self.app.app_context()
        self.ctx.push()

    def post_process_message(self) -> None:
        self.ctx.pop()
