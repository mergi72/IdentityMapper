# IdentityMapper Implementer's Guide

This guide explains how to write a compatible IdentityMapper implementation.

It is practical guidance, not a protocol RFC. The protocol rules are defined
by the RFC documents.

Main rule:

```text
A compatible implementation can be written without reading the Python source
code.
```

## Before You Implement

Start with the protocol boundary:

```text
Source Proof
      |
      v
Source Provider
      |
      v
Canonical Identity
      |
      v
Target Identity Mapper
      |
      v
TargetIdentity
      |
      v
Target Identity Resolver
      |
      v
TargetIdentityResolution
```

The implementation must preserve this boundary.

Do not begin by connecting two systems directly. Begin by defining how each
system speaks to the canonical `Identity` model.

## 1. Source Provider

A source provider reduces source-world proof into canonical `Identity`.

Input:

```text
Identification
Credential
```

Output:

```text
Identity
```

A source provider may internally use:

- passwords
- API keys
- bearer tokens
- certificates
- Kerberos tickets
- SAML assertions
- guest sessions
- local runtime identity

But the output must be canonical `Identity`.

### Source Provider Requirements

A source provider must:

- verify the source proof before producing `Identity`
- reject invalid proof
- keep source implementation details out of `Identity`
- avoid target-specific fields in `Identity`
- avoid knowing which target mapper will consume the identity

### Source Provider Must Not

A source provider must not:

- call a target mapper directly
- call a target resolver directly
- return `TargetIdentity`
- include credential values in `Identity`
- require target selection to verify source proof
- persist credential values

## 2. Target Identity Mapper

A target identity mapper projects canonical `Identity` into a target-world
representation.

Input:

```text
Identity
Target request
```

Output:

```text
TargetIdentity
```

The mapper answers:

```text
How does this canonical Identity look in the target world?
```

It does not answer:

```text
Does this account exist in the target world?
```

That belongs to a target resolver.

### Target Mapper Requirements

A target mapper must:

- consume canonical `Identity`
- consume target request data
- produce `TargetIdentity`
- treat `TargetIdentity` as projection, not proof
- remain deterministic for the same input

### Target Mapper Must Not

A target mapper must not:

- receive source credential values
- receive source provider implementation objects
- authenticate users
- authorize users
- issue tokens
- create sessions
- perform bind or login
- confirm target account existence
- mutate canonical `Identity`

## 3. Target Identity Resolver

A target identity resolver performs read-only target-world lookup for a
projected `TargetIdentity`.

Input:

```text
TargetIdentity
```

Output:

```text
TargetIdentityResolution
```

The resolver answers:

```text
Does this projected target identity resolve in the target world?
```

### Target Resolver Requirements

A target resolver may:

- perform read-only lookup
- return existence state
- return target-world metadata
- return lookup error state

A target resolver must:

- consume only `TargetIdentity`
- return `TargetIdentityResolution`
- keep source credential values out of resolution state
- avoid changing canonical `Identity`

### Target Resolver Must Not

A target resolver must not:

- receive source credential values
- receive source provider implementation objects
- create sessions
- perform login
- perform bind as proof of authentication
- mutate canonical `Identity`

## 4. Credential Handling

Credential values may exist during request processing.

They must not become part of protocol state.

Credential values must not appear in:

- `Identity`
- `TargetIdentity`
- `TargetIdentityResolution`
- audit logs
- cache
- files
- databases

Allowed:

```text
Credential exists in memory during request processing.
```

Forbidden:

```text
Credential is persisted, logged, projected, or passed to target mappers.
```

## 5. Compliance Checklist

Before claiming compatibility, verify:

- valid source proof produces canonical `Identity`
- invalid source proof is rejected
- target mapper consumes only `Identity` and target request
- target mapper produces `TargetIdentity`
- target resolver consumes only `TargetIdentity`
- target resolver produces `TargetIdentityResolution`
- source and target implementations never communicate directly
- credential values are not present in protocol outputs
- adding a new source does not require changing target mappers
- adding a new target mapper does not require changing source providers

## 6. Forbidden Shortcuts

The following shortcuts break the protocol:

```text
Kerberos -> LDAP
OAuth    -> Windows
Basic    -> local_user
```

The correct shape is:

```text
Kerberos -> Identity -> LDAP TargetIdentity
OAuth    -> Identity -> Windows TargetIdentity
Basic    -> Identity -> local_user TargetIdentity
```

Do not pass implementation objects across the boundary.

Do not let source code know target code.

Do not let target code know source code.

## 7. Minimal Implementation Shape

A minimal compatible implementation has:

```text
Source Provider
Target Identity Mapper
Target Identity Resolver
Compliance tests
```

It does not need:

- HTTP
- CLI
- database
- real LDAP server
- real Kerberos KDC
- production identity provider
- credential storage

Those are integration concerns, not protocol requirements.

## Related Documents

- [RFC 0001: IdentityMapper Protocol](rfcs/0001-identitymapper-protocol.md)
- [RFC 0002: IdentityMapper Compliance Suite](rfcs/0002-compliance-suite.md)
- [RFC 0003: IdentityMapper Protocol Versioning](rfcs/0003-protocol-versioning.md)
- [Compliance badge](compliance-badge.md)

