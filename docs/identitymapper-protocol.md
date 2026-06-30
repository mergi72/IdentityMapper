# IdentityMapper Protocol - Design Principles

IdentityMapper is not an LDAP wrapper, OAuth wrapper, or authentication
server. It defines a protocol for translating identity proofs into a canonical
identity and projecting that identity into target identity worlds.

This document describes the protocol principles. It is not a formal standard.
The Python package in this repository is a reference implementation.

## Core Flow

```text
Source Proof
      |
      v
Source Provider
      |
      v
canonical Identity
      |
      v
Target Identity Mapper
      |
      v
TargetIdentity
```

## Principles

1. A source provider receives a proof, assertion, or credential and produces a
   canonical `Identity`.
2. A target identity mapper receives only the canonical `Identity` and a target
   request.
3. A target identity mapper produces a `TargetIdentity` projection for one
   target world.
4. Source providers and target identity mappers never communicate directly.
5. `Identity` is the only shared model between source and target worlds.
6. Adding a new source provider must not require changing target mappers.
7. Adding a new target identity mapper must not require changing source
   providers.
8. Adding a new source or target must not require changing the core domain
   model.

## Boundary

The source side ends at `Identity`.

The target side starts from `Identity`.

```text
Source Provider -> Identity -> Target Identity Mapper
```

The target identity mapper does not receive:

- source credential values
- source provider results
- source implementation models
- authentication sessions
- transport payloads

It receives:

- canonical `Identity`
- target request

## Not A Direct Translation Matrix

IdentityMapper does not define direct mappings such as:

```text
Kerberos -> LDAP
OAuth    -> Windows
SAML     -> API Key
```

Every translation goes through the canonical model:

```text
Kerberos -> Identity -> LDAP TargetIdentity
OAuth    -> Identity -> Windows TargetIdentity
SAML     -> Identity -> API Key TargetIdentity
```

This keeps the mapping model linear:

```text
Sources -> Identity -> Targets
```

instead of explosive:

```text
Sources x Targets
```

## Verification

The reference implementation verifies the protocol boundary with all-to-all
projection tests:

```text
every source provider x every target identity mapper
```

The tests prove that every included source provider can produce a canonical
`Identity`, and every included target mapper can project that `Identity`
without knowing which source provider produced it.

The all-to-all tests intentionally use the boundary directly:

```text
source authenticator -> Identity
target mapper        -> TargetIdentity
```

They do not pass source provider results into target mappers.

## Design Constraint

IdentityMapper must not become a credential manager, identity store, session
manager, authorization engine, or target system client.

Its responsibility is the protocol boundary:

```text
proof -> Identity -> TargetIdentity
```

