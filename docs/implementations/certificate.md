# Client Certificate / mTLS Implementation

## Implementation Model

- `ClientCertificateRequest`
- `ClientCertificateRecord`

## Identification

| Implementation field | Domain field |
| --- | --- |
| `fingerprint` | `Identification.identifier` |
| configured realm | `Identification.realm` |
| `subject` | `Identification.attributes["subject"]` |
| `issuer` | `Identification.attributes["issuer"]` |
| `serial_number` | `Identification.attributes["serial_number"]` |

## Credential

| Implementation field | Domain field |
| --- | --- |
| `proof` | `Credential.value` |
| `"CERTIFICATE_PROOF"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Implementation field | Domain field |
| --- | --- |
| `fingerprint` | `IdentityCandidate.implementation_id` |
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

Client Certificate / mTLS reduces to the identity invariant without requiring a
core model change.
