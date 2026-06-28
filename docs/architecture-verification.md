# Architecture Verification

IdentityMapper has been tested against multiple identity implementation
models. Each implementation maps to the same core invariant without changing
the core domain model or capability contracts.

## Hypothesis

The identity domain can be reduced to one stable invariant.

## Method

Implement independent identity models and reduce each of them to the same core
domain model.

## Core Files

The core files are:

- `src/identity_mapper/domain.py`
- `src/identity_mapper/capabilities.py`
- `src/identity_mapper/mapper.py`

## Verified Flow

```text
Identification
        +
Credential
        |
        v
ResolveIdentity
        |
        v
IdentityCandidate
        |
        v
VerifyCredential
        |
        v
Identity
```

## Result

| Version | Provider | Core changed |
| --- | --- | --- |
| v0.2.0 | BasicAuth | No |
| v0.3.0 | LDAP | No |
| v0.4.0 | OAuth | No |
| v0.5.0 | API Key | No |
| v0.6.0 | JWT / Bearer Token | No |
| v0.7.0 | Client Certificate / mTLS | No |
| v0.8.0 | Kerberos | No |
| v0.9.0 | SAML | No |
| v0.10.0 | Windows / AD SID | No |
| v0.11.0 | LDAP alignment | No |
| v0.12.0 | WebAuthn / FIDO2 | No |
| v0.13.0 | Passkeys | No |
| v0.14.0 | MFA | No |
| v0.15.0 | Federated Identity | No |
| v0.16.0 | Guest / Anonymous Identity | No |

## Verified Providers

- BasicAuth
- LDAP
- OAuth
- JWT / Bearer Token
- API Key
- Client Certificate / mTLS
- Kerberos
- SAML
- Windows / AD SID
- WebAuthn / FIDO2
- Passkeys
- MFA
- Federated Identity
- Guest / Anonymous Identity

## Observation

The tested providers cover passwords, tokens, API keys, certificates,
tickets, assertions, SIDs, WebAuthn credentials, passkeys, multi-factor
credentials, federated trust mappings, and guest sessions.

No provider introduced a new core concept.

## Conclusion

The core domain model remained unchanged.
