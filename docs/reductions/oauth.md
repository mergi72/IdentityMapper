# OAuth Reduction Matrix

## Implementation Model

- `OAuthTokenRequest`
- `OAuthTokenRecord`

## Identification

| Implementation field | Domain field |
| --- | --- |
| `subject` | `Identification.identifier` |
| `issuer` | `Identification.realm` |
| `audience` | `Identification.attributes["audience"]` |

## Credential

| Implementation field | Domain field |
| --- | --- |
| `access_token` | `Credential.value` |
| `"BEARER_TOKEN"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Implementation field | Domain field |
| --- | --- |
| `token_id` | `IdentityCandidate.implementation_id` |
| resolved identification | `IdentityCandidate.identification` |
| `attributes` | `IdentityCandidate.attributes` |

## Identity

| Implementation field | Domain field |
| --- | --- |
| `identity_id` | `Identity.id` |
| `display_name` | `Identity.display_name` |
| `email` | `Identity.email` |
| `scopes` | `Identity.roles` |
| `claims` | `Identity.claims` |
| `attributes` | `Identity.attributes` |
