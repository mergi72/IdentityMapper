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

The provider capability contract is tested in:

- `tests/test_provider_capability_contracts.py`

The automated CI workflow is defined in:

- `.github/workflows/ci.yml`

## Architecture Contract Verification

Every provider must satisfy the same capability contract.

The test suite verifies:

- mapper returns `Identification` and `Credential`
- resolver returns `IdentityCandidate`, not `Identity`
- resolver returns `None` for an unknown identification
- verifier accepts a valid credential
- verifier rejects an invalid credential
- authenticator returns `Identity`
- authenticator rejects an invalid credential with `AuthenticationRejected`
- host service does not treat unexpected `ValueError` as authentication rejection
- host service can select a provider without changing the core domain model
- host service exposes `Authenticate`, `ResolveIdentity`, and `VerifyCredential`
  through the same request/response boundary
- host service records capability invocations without logging credential values
- source identity proof maps to target identity worlds only after producing a
  verified `Identity`
- every source provider can map to every target provider through `Identity`,
  including mapping to itself
- the Windows / AD target mapper produces an AD projection without bind, lookup,
  network calls, service accounts, or account existence confirmation

This is an architectural test. It does not prove that a concrete external
system is integrated correctly. It proves that every provider implementation in
this repository follows the same invariant and capability contract.

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
| v0.20.0 | Provider capability contracts | No |
| v0.28.0 | MapIdentity capability | No |
| v0.28.1 | Provider-to-provider mapping contracts | No |
| v0.29.0 | Windows / AD target projection | No |

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

All providers satisfy the same capability contract.

Version `v0.20.0` is the first release where that contract is expressed directly
in code.

Version `v0.21.0` adds CI for the verified contract suite and Python bytecode
compilation. Linting and formatting are intentionally deferred until their
rules are configured and verified against the existing codebase.

Version `v0.28.1` verifies that every included source provider can map to every
included target provider through a verified `Identity`.

Version `v0.29.0` adds the first concrete target mapper: a projection from
canonical `Identity` to a Windows / AD target shape. The target projection does
not perform AD lookup or account verification.

## Conclusion

The core domain model and capability contract remained unchanged.
