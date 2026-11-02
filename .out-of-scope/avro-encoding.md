# Avro (schema-based) message encoding

Relé serialises published messages as JSON (`json.dumps` with a configurable
`JSONEncoder` subclass) and parses consumed messages with `json.loads`. It does
not support Avro or Pub/Sub schema-enforced topics.

## Why this is out of scope

Avro support is not a serialiser swap. It needs a pluggable codec on the publish
side, a matching decoder on the consume side, schema registration and
evolution, and a different `encoder` configuration surface (today
`ENCODER_PATH` is typed as `type[json.JSONEncoder]`). That is a large change to
the core of a library whose whole premise is "JSON in, JSON out, declare a
function". Since 2022 a single external request has asked for it.

The first, much smaller step is a configurable deserializer on the consume side
(issue #229, PR #230), which lets a project read non-JSON payloads with its own
function. If several projects end up needing schema-based encoding on top of
that, this decision can be revisited with real use cases.

## Prior requests

- #217: "Avro support"
