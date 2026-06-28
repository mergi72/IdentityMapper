# Identity

`Identity` is the verified domain result.

It is the identity invariant used by business logic after successful
authentication.

## Fields

| Field | Meaning |
| --- | --- |
| `id` | Domain identity identifier. |
| `display_name` | Optional human-readable name. |
| `email` | Optional email address. |
| `roles` | Domain roles. |
| `claims` | Domain claims. |
| `attributes` | Additional domain attributes. |

## Role

```text
VerifyCredential
       |
       v
Identity
```

Identity answers:

> Which verified domain identity can the system trust?
