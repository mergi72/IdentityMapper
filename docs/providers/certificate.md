# Client Certificate / mTLS Provider

## Provider Model

- `ClientCertificateRequest`
- `ClientCertificateRecord`

## Identification

| Provider field | Domain field |
| --- | --- |
| `fingerprint` | `Identification.identifier` |
| provider realm | `Identification.realm` |
| `subject` | `Identification.attributes["subject"]` |
| `issuer` | `Identification.attributes["issuer"]` |
| `serial_number` | `Identification.attributes["serial_number"]` |

## Credential

| Provider field | Domain field |
| --- | --- |
| `proof` | `Credential.value` |
| `"CERTIFICATE_PROOF"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Provider field | Domain field |
| --- | --- |
| `fingerprint` | `IdentityCandidate.implementation_id` |
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

Client Certificate / mTLS reduces to the identity invariant without requiring a
core model change.
