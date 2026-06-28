# Federated Identity Provider

## Provider Model

- `FederatedRequest`
- `FederatedIdentityRecord`

## Identification

| Provider field | Domain field |
| --- | --- |
| `external_subject` | `Identification.identifier` |
| `issuer` | `Identification.realm` |
| `issuer` | `Identification.attributes["issuer"]` |
| `audience` | `Identification.attributes["audience"]` |

## Credential

| Provider field | Domain field |
| --- | --- |
| `assertion` | `Credential.value` |
| `"FEDERATION_ASSERTION"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Provider field | Domain field |
| --- | --- |
| `trust_mapping_id` | `IdentityCandidate.implementation_id` |
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

Federated Identity reduces to the identity invariant without requiring a core
model change.
