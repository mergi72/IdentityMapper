# Compatibility Matrix

The compatibility matrix verifies that every included source provider can
produce a canonical `Identity`, and every included target identity mapper can
project that `Identity` into its target world.

This is not a direct implementation-to-implementation matrix.

Every verified path uses the protocol boundary:

```text
Source Provider -> canonical Identity -> Target Identity Mapper
```

## Current Coverage

The reference implementation currently verifies:

```text
14 source providers x 14 target identity mappers = 196 projections
```

The all-to-all coverage is guarded by
`tests/test_provider_capability_contracts.py`.

## Provider Worlds

| World | Source provider | Target identity mapper | All-to-all projection |
| --- | --- | --- | --- |
| BasicAuth | verified | verified | verified |
| LDAP | verified | verified | verified |
| OAuth | verified | verified | verified |
| JWT / Bearer Token | verified | verified | verified |
| API Key | verified | verified | verified |
| Client Certificate / mTLS | verified | verified | verified |
| Kerberos | verified | verified | verified |
| SAML | verified | verified | verified |
| Windows / AD SID | verified | verified | verified |
| WebAuthn / FIDO2 | verified | verified | verified |
| Passkeys | verified | verified | verified |
| MFA | verified | verified | verified |
| Federated Identity | verified | verified | verified |
| Guest / Anonymous Identity | verified | verified | verified |

## Example Paths

| Source proof | Canonical model | Target projection | Status |
| --- | --- | --- | --- |
| BasicAuth | Identity | BasicAuth TargetIdentity | verified |
| BasicAuth | Identity | API Key TargetIdentity | verified |
| BasicAuth | Identity | Guest TargetIdentity | verified |
| API Key | Identity | BasicAuth TargetIdentity | verified |
| API Key | Identity | Windows / AD SID TargetIdentity | verified |
| Guest / Anonymous Identity | Identity | API Key TargetIdentity | verified |
| Kerberos | Identity | Windows / AD SID TargetIdentity | verified |
| JWT / Bearer Token | Identity | LDAP TargetIdentity | verified |
| SAML | Identity | OAuth TargetIdentity | verified |

## What Verified Means

`verified` means:

- the source provider can produce canonical `Identity`
- the target identity mapper can project that `Identity`
- the target identity mapper does not know the source provider
- no source credential value is passed into the target mapper
- no core domain model change was required

It does not mean that an external production system has been contacted.

The target projection is a representation of identity for a target world. It is
not proof that a target account exists.

