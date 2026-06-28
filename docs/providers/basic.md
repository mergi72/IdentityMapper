# BasicAuth Provider

## Provider Model

- `BasicAuthenticationRequest`
- `BasicUserRecord`

## Identification

| Provider field | Domain field |
| --- | --- |
| `username` | `Identification.identifier` |
| `realm` | `Identification.realm` |

## Credential

| Provider field | Domain field |
| --- | --- |
| `password` | `Credential.value` |
| `"PASSWORD"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Provider field | Domain field |
| --- | --- |
| `implementation_id` | `IdentityCandidate.implementation_id` |
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

BasicAuth reduces to the identity invariant without requiring a core model
change.
