# OAuth Provider

## Provider Model

- `OAuthTokenRequest`
- `OAuthTokenRecord`

## Identification

| Provider field | Domain field |
| --- | --- |
| `subject` | `Identification.identifier` |
| `issuer` | `Identification.realm` |
| `audience` | `Identification.attributes["audience"]` |

## Credential

| Provider field | Domain field |
| --- | --- |
| `access_token` | `Credential.value` |
| `"BEARER_TOKEN"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Provider field | Domain field |
| --- | --- |
| `token_id` | `IdentityCandidate.implementation_id` |
| resolved identification | `IdentityCandidate.identification` |
| `attributes` | `IdentityCandidate.attributes` |

## Identity

| Provider field | Domain field |
| --- | --- |
| `identity_id` | `Identity.id` |
| `display_name` | `Identity.display_name` |
| `email` | `Identity.email` |
| `scopes` | `Identity.roles` |
| `claims` | `Identity.claims` |
| `attributes` | `Identity.attributes` |

## Reduction

OAuth reduces to the identity invariant without requiring a core model change.
