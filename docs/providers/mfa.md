# MFA Provider

## Provider Model

- `MfaRequest`
- `MfaFactor`
- `MfaRecord`

## Identification

| Provider field | Domain field |
| --- | --- |
| `identifier` | `Identification.identifier` |
| `realm` | `Identification.realm` |

## Credential

| Provider field | Domain field |
| --- | --- |
| encoded `factors` | `Credential.value` |
| `"MFA_FACTORS"` | `Credential.type` |
| `metadata` + `factor_count` | `Credential.metadata` |

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

MFA reduces to the identity invariant without requiring a core model change.
