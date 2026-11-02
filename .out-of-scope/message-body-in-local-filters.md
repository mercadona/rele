# Passing the message body to `filter_by` predicates

Local `filter_by` predicates receive the message **attributes** (a dict), not
the decoded body. Relé is not going to change that signature.

## Why this is out of scope

The predicate signature `filter(attributes: dict) -> bool` is public API used
by every project with local filters; adding the body changes it for all of
them, and keeping both shapes means inspecting callables at runtime. Local
filters were designed to mirror Pub/Sub's own server-side filtering
(`backend_filter_by`), which by definition only sees attributes: a predicate
that needs the body is business logic, not routing.

What the original request wanted (logging every message, including the ones
the filter drops) is already available: the `pre_process_message` middleware
hook receives the full `message` before filtering. And if you need the body to
decide whether to process, do it at the top of the subscription function and
return early.

## Prior requests

- #85: "Pass complete message body to filter_by (Subscriptions)"
