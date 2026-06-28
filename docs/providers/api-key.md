# API Key Provider

## Provider Model

- `ApiKeyRequest`
- `ApiKeyRecord`

## Identification

| Provider field | Domain field |
| --- | --- |
| `key_id` | `Identification.identifier` |
| provider realm | `Identification.realm` |
| `client_id` | `Identification.attributes["client_id"]` |

## Credential

| Provider field | Domain field |
| --- | --- |
| `api_key` | `Credential.value` |
| `"API_KEY"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Provider field | Domain field |
| --- | --- |
| `key_id` | `IdentityCandidate.implementation_id` |
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

API Key reduces to the identity invariant without requiring a core model change.
