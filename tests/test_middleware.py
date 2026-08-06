import re
import warnings
from unittest.mock import patch

import pytest

import rele
from rele.middleware import DEPRECATED_HOOKS, BaseMiddleware, run_middleware_hook


def _build_middleware_with_post_publish():
    """Builds a middleware that still implements the deprecated post_publish hook.

    The class is created inside a warnings guard because defining a deprecated
    hook triggers the DeprecationWarning from WarnDeprecatedHooks.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)

        class DeprecatedHookMiddleware(BaseMiddleware):
            def __init__(self):
                self.post_publish_calls = []
                self.pre_publish_calls = []

            def post_publish(self, topic):
                self.post_publish_calls.append(topic)

            def pre_publish(self, topic, data, attrs):
                self.pre_publish_calls.append((topic, data, attrs))

    return DeprecatedHookMiddleware()


class MiddlewareWithoutPostPublish(BaseMiddleware):
    def __init__(self):
        self.pre_publish_calls = []

    def pre_publish(self, topic, data, attrs):
        self.pre_publish_calls.append((topic, data, attrs))


class TestMiddleware:
    @pytest.fixture
    def mock_init_global_publisher(self):
        with patch("rele.config.init_global_publisher", autospec=True) as m:
            yield m

    @pytest.mark.usefixtures("mock_init_global_publisher")
    @patch("rele.contrib.FlaskMiddleware.setup", autospec=True)
    def test_setup_fn_is_called_with_kwargs(self, mock_middleware_setup, project_id):
        settings = {
            "GC_PROJECT_ID": project_id,
            "MIDDLEWARE": ["rele.contrib.FlaskMiddleware"],
        }

        rele.setup(settings, foo="bar")
        assert mock_middleware_setup.called
        assert mock_middleware_setup.call_args_list[0][-1] == {"foo": "bar"}

    def test_warns_about_deprecated_hooks(self):
        with pytest.warns(
            DeprecationWarning,
            match=re.escape(
                "The post_publish hook in the middleware is deprecated "
                "and will be removed in future versions. Please substitute it with "
                "the post_publish_success hook instead."
            ),
        ):

            class TestMiddleware(BaseMiddleware):
                def post_publish(self, topic):
                    pass

    def test_deprecated_hook_warning_names_the_actual_hook_and_replacement(self):
        """With a single entry, a hard-coded message happens to read correctly.

        Add a second deprecated hook to prove the warning text is derived
        from the hook that was actually defined, not hard-coded to
        "post_publish"/"post_publish_success" regardless of which hook fired.
        """
        with patch.dict(
            DEPRECATED_HOOKS, {"pre_process_message": "pre_process_message_v2"}
        ):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")

                class TestMiddleware(BaseMiddleware):
                    def pre_process_message(self, subscription, message):
                        pass

            messages = [str(w.message) for w in caught]
            assert any("pre_process_message_v2" in m for m in messages)
            assert not any("post_publish" in m for m in messages)


class TestRunMiddlewareHook:
    @pytest.fixture
    def registered(self):
        """Registers middlewares for the duration of a single test."""
        middlewares = []
        with patch("rele.middleware._middlewares", middlewares):
            yield middlewares

    def test_calls_deprecated_hook_when_middleware_implements_it(self, registered):
        middleware = _build_middleware_with_post_publish()
        registered.append(middleware)

        run_middleware_hook("post_publish", "some-topic")

        assert middleware.post_publish_calls == ["some-topic"]

    def test_skips_deprecated_hook_when_middleware_does_not_implement_it(
        self, registered
    ):
        middleware = MiddlewareWithoutPostPublish()
        registered.append(middleware)
        assert not hasattr(middleware, "post_publish")

        # Must not raise AttributeError: the hook is silently skipped.
        run_middleware_hook("post_publish", "some-topic")

        run_middleware_hook("pre_publish", "some-topic", {}, {})
        assert middleware.pre_publish_calls == [("some-topic", {}, {})]

    def test_calls_deprecated_hook_only_on_middlewares_that_implement_it(
        self, registered
    ):
        implementing = _build_middleware_with_post_publish()
        not_implementing = MiddlewareWithoutPostPublish()
        registered.extend([not_implementing, implementing])

        run_middleware_hook("post_publish", "some-topic")

        assert implementing.post_publish_calls == ["some-topic"]

    def test_forwards_args_and_kwargs_to_every_middleware(self, registered):
        first = _build_middleware_with_post_publish()
        second = MiddlewareWithoutPostPublish()
        registered.extend([first, second])

        run_middleware_hook("pre_publish", "some-topic", {"foo": "bar"}, attrs={})

        assert first.pre_publish_calls == [("some-topic", {"foo": "bar"}, {})]
        assert second.pre_publish_calls == [("some-topic", {"foo": "bar"}, {})]

    def test_raises_when_a_non_deprecated_hook_is_missing(self, registered):
        registered.append(MiddlewareWithoutPostPublish())

        with pytest.raises(AttributeError):
            run_middleware_hook("not_a_hook")

    def test_does_nothing_when_no_middleware_is_registered(self, registered):
        run_middleware_hook("post_publish", "some-topic")
        run_middleware_hook("pre_publish", "some-topic", {}, {})
