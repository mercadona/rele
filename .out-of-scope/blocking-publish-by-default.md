# Blocking publish as the default

Relé keeps `blocking=False` as the default for `publish()`. The setting
`PUBLISHER_BLOCKING` (added in PR #234) lets each project flip the default for
itself.

## Why this is out of scope

Switching the default is a backwards-incompatible change for every caller that
relies on `publish()` returning immediately, so it can only ship in a new major
version. There is no 2.0 planned, and the project policy is not to open a major
for a one-line default when the same result is one setting away:

```python
RELE = {
    ...
    "PUBLISHER_BLOCKING": True,
}
```

If a 2.0 is ever planned, this is a candidate for its changelog; until then the
decision is to keep the current default.

## Prior requests

- #203: "Default publishing to blocking"
