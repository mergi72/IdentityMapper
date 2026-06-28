# Passkeys Reduction Matrix

## Implementation Model

- `PasskeyRequest`
- `PasskeyRecord`

## Identification

| Implementation field | Domain field |
| --- | --- |
| `passkey_id` | `Identification.identifier` |
| `relying_party_id` | `Identification.realm` |
| `user_handle` | `Identification.attributes["user_handle"]` |
| `device_name` | `Identification.attributes["device_name"]` |

## Credential

| Implementation field | Domain field |
| --- | --- |
| `assertion` | `Credential.value` |
| `"PASSKEY_ASSERTION"` | `Credential.type` |
| `metadata` | `Credential.metadata` |

## Candidate

| Implementation field | Domain field |
| --- | --- |
| `passkey_id` | `IdentityCandidate.implementation_id` |
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
