# Kerberos Reduction Matrix

## Implementation Model

- `KerberosRequest`
- `KerberosPrincipalRecord`

## Identification

| Implementation field | Domain field |
| --- | --- |
| `principal` | `Identification.identifier` |
| `realm` | `Identification.realm` |
| `service` | `Identification.attributes["service"]` |

## Credential

| Implementation field | Domain field |
| --- | --- |
| `ticket` | `Credential.value` |
| `"KERBEROS_TICKET"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Implementation field | Domain field |
| --- | --- |
| `principal` | `IdentityCandidate.implementation_id` |
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
