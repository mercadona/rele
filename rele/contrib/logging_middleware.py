import json
import logging
import time
from typing import TYPE_CHECKING, Any

from rele.middleware import BaseMiddleware

if TYPE_CHECKING:
    from rele.config import Config
    from rele.subscription import Subscription


class LoggingMiddleware(BaseMiddleware):
    """Default logging middleware.

    Logging format has been configured for Prometheus.
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def setup(self, config: "Config", **kwargs: Any) -> None:
        self._logger = logging.getLogger(__name__)
        self._app_name: str | None = config.app_name
        self._encoder: type[json.JSONEncoder] = config.encoder

    def _build_data_metrics(
        self,
        subscription: "Subscription",
        message: Any,
        status: str,
        start_processing_time: float | None = None,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "agent": self._app_name,
            "topic": subscription.topic,
            "status": status,
            "subscription": subscription.name,
            "attributes": dict(message.attributes),
        }

        if start_processing_time is not None:
            end_processing_time = time.time()
            result["duration_seconds"] = round(
                end_processing_time - start_processing_time, 3
            )

        return result

    def pre_publish(self, topic: str, data: Any, attrs: dict[str, Any]) -> None:
        self._logger.debug(
            f"Publishing to {topic}",
            extra={
                "pubsub_publisher_attrs": attrs,
                "metrics": {
                    "name": "publications",
                    "data": {"agent": self._app_name, "topic": topic},
                },
            },
        )

    def post_publish_success(
        self, topic: str, data: Any, attrs: dict[str, Any]
    ) -> None:
        self._logger.info(
            f"Successfully published to {topic}",
            extra={
                "pubsub_publisher_attrs": attrs,
                "metrics": {
                    "name": "publications",
                    "data": {"agent": self._app_name, "topic": topic},
                },
            },
        )

    def post_publish_failure(
        self, topic: str, exception: Exception, message: Any
    ) -> None:
        self._logger.exception(
            f"Exception raised while publishing message "
            f"for {topic}: {exception.__class__.__name__!s}",
            exc_info=True,
            extra={
                "metrics": {
                    "name": "publications",
                    "data": {"agent": self._app_name, "topic": topic},
                },
                "subscription_message": json.dumps(message, cls=self._encoder),
            },
        )

    def pre_process_message(self, subscription: "Subscription", message: Any) -> None:
        self._logger.debug(
            f"Start processing message for {subscription}",
            extra={
                "metrics": {
                    "name": "subscriptions",
                    "data": self._build_data_metrics(subscription, message, "received"),
                }
            },
        )

    def post_process_message_success(
        self, subscription: "Subscription", start_time: float, message: Any
    ) -> None:
        self._logger.info(
            f"Successfully processed message for {subscription}",
            extra={
                "metrics": {
                    "name": "subscriptions",
                    "data": self._build_data_metrics(
                        subscription, message, "succeeded", start_time
                    ),
                }
            },
        )

    def post_process_message_failure(
        self,
        subscription: "Subscription",
        exception: Exception,
        start_time: float,
        message: Any,
    ) -> None:
        self._logger.error(
            f"Exception raised while processing message "
            f"for {subscription}: {exception.__class__.__name__!s}",
            exc_info=True,
            extra={
                "metrics": {
                    "name": "subscriptions",
                    "data": self._build_data_metrics(
                        subscription, message, "failed", start_time
                    ),
                },
                "subscription_message": str(message),
            },
        )

    def pre_worker_stop(self, subscriptions: list["Subscription"]) -> None:
        self._logger.info(f"Cleaning up {len(subscriptions)} subscription(s)...")
