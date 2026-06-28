# LDAP Reduction Matrix

## Implementation Model

- `LdapBindRequest`
- `LdapEntry`

## Identification

| Implementation field | Domain field |
| --- | --- |
| `uid` | `Identification.identifier` |
| `realm` | `Identification.realm` |

## Credential

| Implementation field | Domain field |
| --- | --- |
| `password` | `Credential.value` |
| `"PASSWORD"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Implementation field | Domain field |
| --- | --- |
| `dn` | `IdentityCandidate.implementation_id` |
| resolved identification | `IdentityCandidate.identification` |
| `attributes` | `IdentityCandidate.attributes` |

## Identity

| Implementation field | Domain field |
| --- | --- |
| `identity_id` | `Identity.id` |
| `cn` | `Identity.display_name` |
| `mail` | `Identity.email` |
| `groups` | `Identity.roles` |
| `claims` | `Identity.claims` |
| `attributes` | `Identity.attributes` |
