# IdentityMapper Compliance Suite

This directory is the starting point for protocol compliance tests.

The compliance suite is defined by:

- [RFC 0001: IdentityMapper Protocol](../docs/rfcs/0001-identitymapper-protocol.md)
- [RFC 0002: IdentityMapper Compliance Suite](../docs/rfcs/0002-compliance-suite.md)

The normal project test suite verifies the Python reference implementation:

```bash
python -m pytest
```

The compliance suite verifies the protocol boundary in a transport-neutral way:

```bash
python -m pytest compliance
```

## Scope

Compliance tests should verify protocol behavior, not provider internals.

They should prove:

- source providers produce canonical `Identity`
- target mappers consume only canonical `Identity`
- target resolvers consume only `TargetIdentity`
- source and target worlds do not communicate directly
- credential values are not persisted or logged by the protocol boundary

## Required Tests

Required compliance tests verify:

- valid source proof produces canonical `Identity`
- invalid source proof is rejected
- target mapper consumes only `Identity` and target request
- target mapper produces `TargetIdentity`
- target resolver consumes only `TargetIdentity`
- target resolver produces `TargetIdentityResolution`
- full protocol flow keeps source and target decoupled
- credential values do not appear in identity, target projection, target
  resolution, or logs

## Optional Tests

Optional compliance tests may verify:

- HTTP transport adapters
- CLI adapters
- audit rendering
- provider footprint files
- integration with concrete external identity systems

Optional tests are useful for a reference implementation, but they are not
required to prove protocol compliance.

## Forbidden Behavior

Compliance tests should fail if an implementation:

- maps source implementation directly to target implementation
- passes source credential values to target mappers
- passes source credential values to target resolvers
- treats `TargetIdentity` projection as account verification
- creates sessions or runtime login contexts during target projection
- performs bind/login as part of `MapIdentity`
- writes credential values to logs, cache, files, or databases

## Non-Scope

Compliance tests must not require:

- LDAP servers
- OAuth servers
- Kerberos KDCs
- Windows domains
- Linux accounts
- network connectivity
- stored credentials

Concrete integrations can add their own integration tests outside this
compliance suite.
