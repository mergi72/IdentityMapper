# TargetIdentity

`TargetIdentity` is a target-specific projection of a verified canonical
`Identity`.

It is not a second source of truth.

```text
Identity
        |
        v
TargetIdentity
```

`TargetIdentity` may contain target-shaped identifiers and hints, such as an AD
UPN candidate or a system-specific account name candidate.

It must not claim that the target account exists unless a separate target
verification capability proves that later.
