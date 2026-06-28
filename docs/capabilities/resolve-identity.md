# ResolveIdentity

`ResolveIdentity` finds an identity candidate from an identification.

It does not verify credentials and it does not return a final `Identity`.

## Contract

```text
ResolveIdentity(Identification) -> IdentityCandidate | None
```

## Rule

Resolution produces a candidate, not a verified identity.
