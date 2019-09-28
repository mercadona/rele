from django import db

from rele.middleware import BaseMiddleware


class DjangoDBMiddleware(BaseMiddleware):
    """Django specific middleware for managing database connections.
    """

    def pre_process_message(self, *args):
        db.close_old_connections()

    def post_process_message(self):
        db.close_old_connections()

    def post_worker_stop(self):
        db.connections.close_all()
