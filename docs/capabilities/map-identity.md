# MapIdentity

`MapIdentity` maps a verified canonical `Identity` into a target identity world.

The capability exists to avoid direct implementation-to-implementation mapping.

```text
Source proof
        |
        v
Source Provider
        |
        v
Identity
        |
        v
Target Mapper
        |
        v
TargetIdentity
```

The source provider validates the source proof and produces `Identity`.

The target mapper receives only:

- the verified `Identity`
- the requested `IdentityTarget`

The target mapper does not receive source credential values and does not call
the source provider.

## Rule

Do not implement:

```text
Kerberos -> AD
```

Implement:

```text
Kerberos proof -> Identity -> AD projection
```

`TargetIdentity` is a projection, not proof that a target account exists.
