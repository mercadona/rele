from django import db

from rele.middleware import BaseMiddleware


class DjangoDBMiddleware(BaseMiddleware):

    def pre_process_message(self, *args):
        db.close_old_connections()

    def post_process_message(self):
        db.close_old_connections()
