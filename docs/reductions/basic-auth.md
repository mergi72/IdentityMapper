# BasicAuth Reduction Matrix

## Implementation Model

- `BasicAuthenticationRequest`
- `BasicUserRecord`

## Identification

| Implementation field | Domain field |
| --- | --- |
| `username` | `Identification.identifier` |
| `realm` | `Identification.realm` |

## Credential

| Implementation field | Domain field |
| --- | --- |
| `password` | `Credential.value` |
| `"PASSWORD"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Implementation field | Domain field |
| --- | --- |
| `implementation_id` | `IdentityCandidate.implementation_id` |
| resolved identification | `IdentityCandidate.identification` |
| `attributes` | `IdentityCandidate.attributes` |

## Identity

| Implementation field | Domain field |
| --- | --- |
| `identity_id` | `Identity.id` |
| `display_name` | `Identity.display_name` |
| `email` | `Identity.email` |
| `roles` | `Identity.roles` |
| `claims` | `Identity.claims` |
| `attributes` | `Identity.attributes` |
