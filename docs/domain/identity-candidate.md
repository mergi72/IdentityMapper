# IdentityCandidate

`IdentityCandidate` is an unverified identity candidate found by
identification.

It is intentionally not the final domain identity.

## Fields

| Field | Meaning |
| --- | --- |
| `implementation_id` | Provider-shaped identifier, such as a DN, subject, SID, key id, or session id. |
| `identification` | The identification that resolved this candidate. |
| `attributes` | Provider attributes available before verification. |

## Role

```text
Identification
       |
       v
IdentityCandidate
       |
       v
VerifyCredential
```

IdentityCandidate answers:

> Which unverified implementation record was found?
