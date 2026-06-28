# SAML Implementation

## Implementation Model

- `SamlRequest`
- `SamlAssertionRecord`

## Identification

| Implementation field | Domain field |
| --- | --- |
| `name_id` | `Identification.identifier` |
| `issuer` | `Identification.realm` |
| `audience` | `Identification.attributes["audience"]` |
| `session_index` | `Identification.attributes["session_index"]` |

## Credential

| Implementation field | Domain field |
| --- | --- |
| `assertion` | `Credential.value` |
| `"SAML_ASSERTION"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Implementation field | Domain field |
| --- | --- |
| `assertion_id` | `IdentityCandidate.implementation_id` |
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

## Reduction

SAML reduces to the identity invariant without requiring a core model change.
