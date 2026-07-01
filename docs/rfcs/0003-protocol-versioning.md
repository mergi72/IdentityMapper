# RFC 0003: IdentityMapper Protocol Versioning

Status: Draft

## Summary

IdentityMapper Protocol versioning defines how protocol compatibility is named,
declared, and evaluated.

The protocol version is separate from the Python reference implementation
version.

## Purpose

An implementation should be able to say:

```text
I implement IdentityMapper Protocol 1.0.
```

That statement must not depend on:

- Python package version
- host transport
- runtime process model
- provider implementation language
- operating system

It depends only on whether the implementation preserves the protocol
contracts.

## Version Names

IdentityMapper uses two version lines:

```text
IdentityMapper Protocol 1.0
Reference Implementation 0.x
```

The protocol version describes compatibility with the protocol contracts.

The reference implementation version describes the Python implementation in
this repository.

## Protocol Version Format

Protocol versions use:

```text
MAJOR.MINOR
```

Patch versions belong to implementations, documents, tests, or compliance
suites. They do not create a new protocol version unless the protocol contract
changes.

Examples:

```text
IdentityMapper Protocol 1.0
IdentityMapper Protocol 1.1
IdentityMapper Protocol 2.0
```

## Major Version

A major protocol version changes when an implementation that was compliant with
the previous major version may no longer be compliant.

Examples of major changes:

- changing the meaning of canonical `Identity`
- requiring target mappers to receive source credential values
- allowing direct source-to-target implementation mapping
- removing a required protocol boundary
- changing `TargetIdentity` from projection to source of truth

Major changes require a new protocol line:

```text
IdentityMapper Protocol 2.0
```

## Minor Version

A minor protocol version changes when the protocol adds compatible rules,
contracts, or optional behavior without breaking existing compliant
implementations.

Examples of minor changes:

- adding an optional protocol artifact
- adding a new optional compliance area
- clarifying existing contract language
- adding a new non-breaking target resolver rule

Minor changes preserve compatibility with the same major version.

## Patch Version

Patch versions are implementation or document versions.

They may include:

- documentation fixes
- compliance suite improvements
- reference implementation fixes
- additional tests
- example updates
- non-contract wording changes

Patch versions must not change protocol meaning.

## Compatibility Statement

A compliant implementation should declare:

```text
protocol: IdentityMapper Protocol 1.0
compliance: passed
implementation: <name> <version>
```

Example:

```text
protocol: IdentityMapper Protocol 1.0
compliance: passed
implementation: identitymapper-python 0.35.2
```

The implementation version may change without changing protocol compatibility.

## Compliance Suite Relationship

The compliance suite must declare which protocol version it evaluates.

Example:

```text
Compliance Suite for IdentityMapper Protocol 1.0
```

A compliance suite patch may improve tests without changing the protocol
version, as long as it does not add new required protocol behavior.

If a compliance suite adds required behavior, the protocol version must be
reviewed.

## Breaking Behavior

The following changes are breaking at the protocol level:

- source providers require knowledge of target mappers
- target mappers require source provider implementation objects
- target resolvers receive source credential values
- credential values become part of `Identity`, `TargetIdentity`, or
  `TargetIdentityResolution`
- direct implementation-to-implementation mapping becomes compliant behavior
- projection starts confirming target account existence

These changes require a major protocol version.

## Non-Breaking Behavior

The following changes are not breaking at the protocol level:

- adding a new source provider
- adding a new target mapper
- adding a new target resolver
- adding a new transport adapter
- adding host service endpoints that preserve protocol boundaries
- adding implementation-specific tests
- improving audit output without logging credential values

These changes may be released as reference implementation changes without a new
protocol version.

## RFC Relationship

RFC 0001 defines the protocol.

RFC 0002 defines compliance.

RFC 0003 defines how protocol compatibility is versioned.

