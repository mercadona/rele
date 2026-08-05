from unittest.mock import MagicMock

import flask
import pytest
from flask.globals import app_ctx

from rele.contrib.flask_middleware import FlaskMiddleware
from tests.subs import sub_stub


@pytest.fixture
def flask_app():
    return flask.Flask("rele-test-app")


@pytest.fixture
def other_flask_app():
    return flask.Flask("some-other-app")


@pytest.fixture
def message():
    return MagicMock()


class TestFlaskMiddleware:
    @pytest.fixture
    def flask_middleware(self, config, flask_app):
        flask_middleware = FlaskMiddleware()
        flask_middleware.setup(config, flask_app=flask_app)
        yield flask_middleware
        # A middleware that leaks its app context would poison every test that
        # runs afterwards, so drain whatever is left on the stack here. This
        # runs after the assertions, so it never hides a leak from them.
        while flask.has_app_context():
            app_ctx.pop()

    def test_setup_keeps_the_flask_app_given_as_kwarg(
        self, flask_middleware, flask_app
    ):
        assert flask_middleware.app is flask_app

    def test_pre_process_message_activates_the_app_context(
        self, flask_middleware, flask_app, message
    ):
        assert not flask.has_app_context()

        flask_middleware.pre_process_message(sub_stub, message)

        assert flask.has_app_context()
        assert flask.current_app._get_current_object() is flask_app

    def test_pre_process_message_pushes_the_context_of_its_own_app(
        self, flask_middleware, flask_app, other_flask_app, message
    ):
        other_ctx = other_flask_app.app_context()
        other_ctx.push()
        try:
            flask_middleware.pre_process_message(sub_stub, message)

            assert flask.current_app._get_current_object() is flask_app
        finally:
            while flask.has_app_context():
                app_ctx.pop()

    def test_post_process_message_deactivates_the_app_context(
        self, flask_middleware, message
    ):
        flask_middleware.pre_process_message(sub_stub, message)
        assert flask.has_app_context()

        flask_middleware.post_process_message()

        assert not flask.has_app_context()

    def test_post_process_message_pops_the_context_pushed_by_pre_process_message(
        self, flask_middleware, message
    ):
        flask_middleware.pre_process_message(sub_stub, message)
        pushed_ctx = app_ctx._get_current_object()

        flask_middleware.post_process_message()

        assert flask_middleware.ctx is pushed_ctx
        assert not flask.has_app_context()

    def test_consecutive_messages_do_not_leak_app_contexts(
        self, flask_middleware, flask_app, message
    ):
        for index in range(3):
            flask_middleware.pre_process_message(sub_stub, message)
            assert flask.current_app._get_current_object() is flask_app

            # Draining the context stack is not enough: a middleware that built
            # one app context in setup() and re-pushed it for every message
            # would also leave the stack empty here, while carrying the previous
            # message's `g` state into this one.
            assert not hasattr(flask.g, "handled_message")
            flask.g.handled_message = index

            flask_middleware.post_process_message()
            assert not flask.has_app_context()

    def test_app_context_is_usable_while_the_message_is_processed(
        self, flask_middleware, flask_app, message
    ):
        flask_middleware.pre_process_message(sub_stub, message)

        assert flask.current_app.name == flask_app.name
        flask.g.processed_by = "rele"
        assert flask.g.processed_by == "rele"

        flask_middleware.post_process_message()

        with pytest.raises(RuntimeError):
            assert flask.g.processed_by
