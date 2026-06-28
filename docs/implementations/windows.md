# Windows / AD SID Implementation

## Implementation Model

- `WindowsIdentityRequest`
- `WindowsIdentityRecord`

## Identification

| Implementation field | Domain field |
| --- | --- |
| `sid` | `Identification.identifier` |
| `domain` | `Identification.realm` |
| `upn` | `Identification.attributes["upn"]` |

## Credential

| Implementation field | Domain field |
| --- | --- |
| `logon_proof` | `Credential.value` |
| `"WINDOWS_LOGON_PROOF"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Implementation field | Domain field |
| --- | --- |
| `sid` | `IdentityCandidate.implementation_id` |
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

Windows / AD SID reduces to the identity invariant without requiring a core
model change.
