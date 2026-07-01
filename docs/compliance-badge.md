# IdentityMapper Compliance Badge

The IdentityMapper Compliance Badge is a human-readable claim that an
implementation preserves the IdentityMapper Protocol boundary.

Example:

```text
IdentityMapper Protocol 1.0 Draft compliant
```

## Meaning

The badge means that an implementation has passed the required compliance tests
for a declared IdentityMapper Protocol version.

For the current draft, the badge means:

```text
Source Provider -> Identity -> TargetIdentity -> TargetIdentityResolution
```

is preserved without direct source-to-target implementation mapping.

## Required Statement

A badge claim should include:

```text
protocol: IdentityMapper Protocol 1.0 Draft
compliance: passed
implementation: <name> <version>
suite: <compliance suite version or commit>
```

Example:

```text
protocol: IdentityMapper Protocol 1.0 Draft
compliance: passed
implementation: identitymapper-python 0.35.3
suite: reference compliance suite
```

## What It Confirms

The badge confirms that the implementation preserves protocol boundaries:

- source proof can produce canonical `Identity`
- target mappers consume canonical `Identity`
- target resolvers consume `TargetIdentity`
- source and target implementations do not communicate directly
- credential values are not persisted by the protocol boundary
- credential values are not present in `Identity`, `TargetIdentity`, or
  `TargetIdentityResolution`

## What It Does Not Confirm

The badge does not mean:

- production security has been audited
- LDAP, OAuth, Kerberos, Windows, or Linux integrations are production-ready
- a real external identity system was tested
- deployment trust policy is correct
- credentials are safely managed outside IdentityMapper
- a host service is hardened
- authorization policy is implemented

The badge is about protocol conformance, not operational security.

## Non-Goals

The badge must not become:

- a replacement for security review
- a replacement for integration testing
- a replacement for deployment hardening
- a claim that all providers are production-grade
- a claim that external identity systems trust each other

## Relationship To Compliance Suite

The badge is backed by the compliance suite described in:

- [RFC 0002: IdentityMapper Compliance Suite](rfcs/0002-compliance-suite.md)
- [RFC 0003: IdentityMapper Protocol Versioning](rfcs/0003-protocol-versioning.md)

An implementation should not claim the badge unless the required compliance
tests pass for the declared protocol version.

## Display

Projects may display a plain text badge:

```text
IdentityMapper Protocol 1.0 Draft compliant
```

or a README badge:

```text
IdentityMapper Protocol 1.0 Draft: compliant
```

The badge text should always include the protocol version or draft name.

