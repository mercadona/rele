from rele.middleware import BaseMiddleware


class FlaskMiddleware(BaseMiddleware):
    def setup(self, config, **kwargs):
        self.app = kwargs["flask_app"]

    def pre_process_message(self, subscription, message):
        self.ctx = self.app.app_context()
        self.ctx.push()

    def post_process_message(self):
        self.ctx.pop()
