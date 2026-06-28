# Guest / Anonymous Identity Reduction Matrix

## Implementation Model

- `GuestRequest`
- `GuestSessionRecord`

## Identification

| Implementation field | Domain field |
| --- | --- |
| `session_id` | `Identification.identifier` |
| `realm` or `"guest"` | `Identification.realm` |
| `"guest"` | `Identification.attributes["kind"]` |

## Credential

| Implementation field | Domain field |
| --- | --- |
| `session_token` | `Credential.value` |
| `"GUEST_SESSION"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Implementation field | Domain field |
| --- | --- |
| `session_id` | `IdentityCandidate.implementation_id` |
| resolved identification | `IdentityCandidate.identification` |
| `attributes` | `IdentityCandidate.attributes` |

## Identity

| Implementation field | Domain field |
| --- | --- |
| `identity_id` | `Identity.id` |
| `display_name` | `Identity.display_name` |
| `roles` | `Identity.roles` |
| `claims` | `Identity.claims` |
| `attributes` | `Identity.attributes` |
