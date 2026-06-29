# IdentityTarget

`IdentityTarget` describes the target identity world requested by a mapping
operation.

It is not a credential, account, session, or proof.

```text
IdentityTarget
  provider
  realm
  purpose
  attributes
```

`provider` selects the target mapper. `realm`, `purpose`, and `attributes`
describe the requested target context.

The target is a routing and projection request. It is not part of the canonical
identity itself.
