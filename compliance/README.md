# IdentityMapper Compliance Suite

This directory is the starting point for protocol compliance tests.

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
