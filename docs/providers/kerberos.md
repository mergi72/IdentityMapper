# Kerberos Provider

## Provider Model

- `KerberosRequest`
- `KerberosPrincipalRecord`

## Identification

| Provider field | Domain field |
| --- | --- |
| `principal` | `Identification.identifier` |
| `realm` | `Identification.realm` |
| `service` | `Identification.attributes["service"]` |

## Credential

| Provider field | Domain field |
| --- | --- |
| `ticket` | `Credential.value` |
| `"KERBEROS_TICKET"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Provider field | Domain field |
| --- | --- |
| `principal` | `IdentityCandidate.implementation_id` |
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

Kerberos reduces to the identity invariant without requiring a core model
change.
