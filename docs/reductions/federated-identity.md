# Federated Identity Reduction Matrix

## Implementation Model

- `FederatedRequest`
- `FederatedIdentityRecord`

## Identification

| Implementation field | Domain field |
| --- | --- |
| `external_subject` | `Identification.identifier` |
| `issuer` | `Identification.realm` |
| `issuer` | `Identification.attributes["issuer"]` |
| `audience` | `Identification.attributes["audience"]` |

## Credential

| Implementation field | Domain field |
| --- | --- |
| `assertion` | `Credential.value` |
| `"FEDERATION_ASSERTION"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Implementation field | Domain field |
| --- | --- |
| `trust_mapping_id` | `IdentityCandidate.implementation_id` |
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
