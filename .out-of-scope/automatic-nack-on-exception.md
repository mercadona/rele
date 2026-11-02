# Automatic nack when a subscription raises

Relé does not nack (or otherwise force an immediate redelivery of) a message
when the subscription callback raises an unhandled exception. The message is
left unacknowledged and Pub/Sub redelivers it when the ack deadline expires.

## Why this is out of scope

This was tried. PR #254 made `Callback` nack on exception and was merged on
2025-06-09; PR #293 reverted it the same day because an immediate nack floods
subscribers that have no exponential-backoff retry policy: the same failing
message comes straight back, as fast as Pub/Sub can deliver it. The default
behaviour has to be safe for every subscription, including the ones that never
configured a `RetryPolicy`.

The two halves of the request already have opt-in homes:

- To **discard** a message that can never succeed, raise
  `UnrecoverableException` with `UnrecoverableMiddleWare` enabled: the
  middleware acks it.
- To **retry** on purpose, a middleware's `post_process_message_failure` hook
  receives the `message` and can call `message.nack()` itself. Issue #196 tracks
  shipping that as a ready-made opt-in middleware.
- Dead-letter topics, the proper destination for messages that keep failing,
  are discussed in #301.

Changing the default again would change retry semantics for every existing
consumer, which is exactly what #293 undid.

## Prior requests

- #80: "Handling unhandled exceptions"
