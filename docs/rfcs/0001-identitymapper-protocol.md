# RFC 0001: IdentityMapper Protocol

Status: Draft

## Summary

IdentityMapper Protocol defines a canonical identity exchange between
heterogeneous identity systems. It does not replace authentication or trust. It
standardizes how verified identity is represented, projected, and resolved
across different identity worlds.

## Purpose

Identity systems commonly expose incompatible implementation models: passwords,
tokens, tickets, certificates, assertions, SIDs, local users, guest sessions,
and federated identities.

IdentityMapper defines the protocol boundary between those worlds:

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

The protocol keeps source systems and target systems from knowing each other
directly.

## Terms

`Identification`

The source-world value used to select a candidate identity.

`Credential`

The source-world proof used by a source provider to verify an identification.
IdentityMapper may carry this value during request processing, but must not
persist it, cache it, or write it to audit logs.

`IdentityCandidate`

An unverified candidate found by a source provider.

`Identity`

The canonical representation produced only after successful source
verification.

`TargetIdentity`

A projection of canonical `Identity` into a target identity world. It is not a
second source of truth.

`TargetIdentityResolution`

A read-only lookup result for a `TargetIdentity` in a target world.

## Source Contract

A source provider accepts source-world input and produces canonical `Identity`.

The contract boundary is:

```text
Identification + Credential -> Identity
```

A source provider must not know which target mapper or target resolver will use
the resulting identity.

## Target Mapper Contract

A target mapper accepts:

- canonical `Identity`
- target request

It produces:

- `TargetIdentity`

A target mapper must not authenticate, authorize, bind, issue sessions, issue
tokens, perform network calls, or confirm account existence.

The contract boundary is:

```text
Identity -> TargetIdentity
```

## Target Resolver Contract

A target resolver accepts:

- `TargetIdentity`

It produces:

- `TargetIdentityResolution`

A target resolver may perform read-only lookup in its target world. It must not
receive source credential values.

The contract boundary is:

```text
TargetIdentity -> TargetIdentityResolution
```

## Mapping Rules

Implementations are never mapped to each other directly.

Wrong:

```text
Kerberos -> LDAP
Basic    -> Ubuntu
OAuth    -> Windows
```

Correct:

```text
Kerberos -> Identity -> LDAP TargetIdentity
Basic    -> Identity -> local_user TargetIdentity
OAuth    -> Identity -> Windows TargetIdentity
```

## Trust Boundary

IdentityMapper does not create trust by itself.

Trust belongs to source providers, target systems, host policy, and deployment
configuration.

IdentityMapper only standardizes the representation and transfer shape:

```text
verified source identity -> canonical Identity -> target projection/resolution
```

## Compatibility Rules

Adding a source provider must not require changing:

- canonical `Identity`
- existing target mappers
- existing target resolvers
- existing source providers

Adding a target mapper or target resolver must not require changing:

- canonical `Identity`
- existing source providers
- existing target mappers
- existing target resolvers

## Non-Goals

IdentityMapper is not:

- a credential manager
- an identity store
- a password vault
- a session manager
- an authorization engine
- an LDAP wrapper
- an OAuth wrapper
- an authentication server
- a replacement for trust policy

## Compliance Requirements

A compliant implementation must demonstrate:

1. A source provider can produce canonical `Identity` from verified source
   proof.
2. A target mapper can project only canonical `Identity` into `TargetIdentity`.
3. A target resolver can resolve only `TargetIdentity` into
   `TargetIdentityResolution`.
4. Source and target implementations do not communicate directly.
5. Credential values are not persisted or logged.
6. Adding a new source or target does not require changing the core domain.

## Reference Implementation

The Python package in this repository is the reference implementation of this
draft protocol.

The protocol is intentionally described independently of Python so another
implementation can preserve the same boundaries in a different language.
