# WebAuthn / FIDO2 Implementation

## Implementation Model

- `WebAuthnRequest`
- `WebAuthnCredentialRecord`

## Identification

| Implementation field | Domain field |
| --- | --- |
| `credential_id` | `Identification.identifier` |
| `relying_party_id` | `Identification.realm` |
| `user_handle` | `Identification.attributes["user_handle"]` |
| `challenge` | `Identification.attributes["challenge"]` |

## Credential

| Implementation field | Domain field |
| --- | --- |
| `assertion` | `Credential.value` |
| `"WEBAUTHN_ASSERTION"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Implementation field | Domain field |
| --- | --- |
| `credential_id` | `IdentityCandidate.implementation_id` |
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

WebAuthn / FIDO2 reduces to the identity invariant without requiring a core
model change.
