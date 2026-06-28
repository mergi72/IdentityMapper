# JWT / Bearer Token Provider

## Provider Model

- `JwtRequest`
- `JwtRecord`

## Identification

| Provider field | Domain field |
| --- | --- |
| `subject` | `Identification.identifier` |
| `issuer` | `Identification.realm` |
| `audience` | `Identification.attributes["audience"]` |

## Credential

| Provider field | Domain field |
| --- | --- |
| `bearer_token` | `Credential.value` |
| `"BEARER_TOKEN"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Provider field | Domain field |
| --- | --- |
| `jwt_id` | `IdentityCandidate.implementation_id` |
| resolved identification | `IdentityCandidate.identification` |
| `attributes` | `IdentityCandidate.attributes` |

## Identity

| Provider field | Domain field |
| --- | --- |
| `identity_id` | `Identity.id` |
| `display_name` | `Identity.display_name` |
| `email` | `Identity.email` |
| `roles` | `Identity.roles` |
| `claims` | `Identity.claims` |
| `attributes` | `Identity.attributes` |

## Reduction

JWT / Bearer Token reduces to the identity invariant without requiring a core
model change.
