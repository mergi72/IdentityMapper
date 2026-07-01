# RFC 0002: IdentityMapper Compliance Suite

Status: Draft

## Summary

The IdentityMapper Compliance Suite defines how an implementation demonstrates
that it follows the IdentityMapper Protocol.

The suite tests protocol boundaries. It does not test production integration
with LDAP, OAuth, Kerberos, Windows domains, Linux accounts, or any other
external identity system.

## Purpose

An implementation should be able to claim compliance without using the Python
reference implementation internally.

The compliance suite answers this question:

```text
Does this implementation preserve the protocol boundary?
```

That boundary is:

```text
Source Provider -> Identity -> TargetIdentity -> TargetIdentityResolution
```

## Required Compliance Areas

### 1. Canonical Identity

An implementation must produce canonical `Identity` only after successful
source verification.

The compliance suite must verify:

- valid source proof produces `Identity`
- invalid source proof is rejected
- `Identification` is not treated as final `Identity`
- credential values are not present in `Identity`

### 2. Source Provider Boundary

A source provider must not know which target mapper or target resolver will
consume the resulting `Identity`.

The compliance suite must verify:

- source provider input ends at canonical `Identity`
- source provider output does not include target-specific runtime state
- target selection is not required to authenticate source proof

### 3. Target Mapper Boundary

A target mapper must consume only:

- canonical `Identity`
- target request

It must produce:

- `TargetIdentity`

The compliance suite must verify:

- target mapper does not receive source credential values
- target mapper does not receive source provider implementation objects
- target mapper does not confirm account existence
- target mapper does not issue sessions, tokens, assertions, or binds

### 4. Target Resolver Boundary

A target resolver must consume only:

- `TargetIdentity`

It must produce:

- `TargetIdentityResolution`

The compliance suite must verify:

- target resolver does not receive source credential values
- target resolver does not receive source provider implementation objects
- target resolver returns read-only resolution state

### 5. Source/Target Decoupling

Source and target implementations must not communicate directly.

The compliance suite must verify the full boundary:

```text
source proof -> Identity -> TargetIdentity -> TargetIdentityResolution
```

without passing source provider internals into target mapper or target
resolver code.

### 6. Credential Handling

Credential values may exist during request processing, but must not be
persisted by IdentityMapper.

The compliance suite must verify:

- credential value is not written to audit output
- credential value is not present in `Identity`
- credential value is not present in `TargetIdentity`
- credential value is not present in `TargetIdentityResolution`

## Optional Compliance Areas

Optional tests may verify:

- HTTP transport adapters
- CLI adapters
- audit formatting
- provider footprint files
- implementation-specific providers
- integration with real external identity systems

These tests are useful, but they are not required for protocol compliance.

## Forbidden Behavior

A compliant implementation must not:

- map implementation A directly to implementation B
- pass source credential values to target mappers
- pass source credential values to target resolvers
- treat target projection as target account verification
- create sessions as part of `MapIdentity`
- perform bind/login as part of target projection
- persist credentials in logs, cache, files, or databases

## Expected Artifacts

A compliance run should produce:

- test result summary
- implementation name and version
- protocol version or draft reference
- compliance suite version
- list of required tests passed or failed

## Reference Suite

The Python reference repository contains the initial compliance suite in:

```text
compliance/
```

It can be run with:

```bash
python -m pytest compliance
```

This suite is intentionally small. It defines the compliance shape before
large implementation-specific adapters are added.

## Relationship To RFC 0001

RFC 0001 defines the protocol.

RFC 0002 defines how an implementation demonstrates conformance to that
protocol.
