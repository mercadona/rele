# Passing arbitrary options to `create_subscription`

Relé does not forward an open-ended dict of options to the Pub/Sub
`create_subscription` / `update_subscription` calls. Each supported option is
an explicit, typed parameter of `@sub` / `Subscription` and of the `RELE`
settings.

## Why this is out of scope

Every Pub/Sub option Relé exposes also has to be *updated* correctly on
subscriptions that already exist (`_update_subscription` builds an explicit
`update_mask`), validated before the call, and documented. A pass-through dict
sidesteps all three, and the subscription silently diverges from the code the
moment an option is only applied at creation time. The project has instead
added options one by one as they were needed: `backend_filter_by` (#207),
`retry_policy` (#243, #252), and dead-letter policy is being discussed in
#301. Per-subscription `ack_deadline` is tracked in #54.

If you need an option Relé does not expose yet, open an issue for that option.

## Prior requests

- #193: "Accept attributes when creating a subscription"
