# Identification

`Identification` is the claim used to select which identity candidate should be
verified.

It is not the final identity.

## Fields

| Field | Meaning |
| --- | --- |
| `identifier` | The implementation-facing value used to find a candidate. |
| `realm` | Optional namespace, issuer, tenant, directory, or provider context. |
| `attributes` | Additional selection metadata. |

## Role

```text
Identification
       |
       v
ResolveIdentity
       |
       v
IdentityCandidate
```

Identification answers:

> Which identity candidate should be resolved?
