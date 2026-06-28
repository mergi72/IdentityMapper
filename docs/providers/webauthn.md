# WebAuthn / FIDO2 Provider

## Provider Model

- `WebAuthnRequest`
- `WebAuthnCredentialRecord`

## Identification

| Provider field | Domain field |
| --- | --- |
| `credential_id` | `Identification.identifier` |
| `relying_party_id` | `Identification.realm` |
| `user_handle` | `Identification.attributes["user_handle"]` |
| `challenge` | `Identification.attributes["challenge"]` |

## Credential

| Provider field | Domain field |
| --- | --- |
| `assertion` | `Credential.value` |
| `"WEBAUTHN_ASSERTION"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Provider field | Domain field |
| --- | --- |
| `credential_id` | `IdentityCandidate.implementation_id` |
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

WebAuthn / FIDO2 reduces to the identity invariant without requiring a core
model change.
