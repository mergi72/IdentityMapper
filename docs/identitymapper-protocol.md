# IdentityMapper Protocol 1.0 Draft

IdentityMapper is not an LDAP wrapper, OAuth wrapper, or authentication
server. It defines a protocol for translating identity proofs into a canonical
identity and projecting that identity into target identity worlds.

This document describes the protocol contract. It is not a formal standard.
The Python package in this repository is a reference implementation.

## Purpose

Identity systems often speak different implementation languages:

- passwords
- tokens
- tickets
- assertions
- certificates
- SIDs
- guest sessions
- federated identities

IdentityMapper defines one shared boundary between those systems:

```text
Proof -> canonical Identity -> TargetIdentity
```

The purpose is not to replace authentication systems. The purpose is to let
heterogeneous identity systems communicate through one canonical identity
model without knowing each other directly.

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

## Canonical Identity

`Identity` is the only shared model between source and target worlds.

It represents the verified identity after a source provider has accepted a
proof, assertion, or credential.

`Identity` must not contain source credential values.

`Identity` must not contain target runtime state such as sessions, binds,
tokens, network connections, or account existence confirmations.

## Source Provider Contract

A source provider receives source-world input and produces canonical
`Identity`.

The source side may use implementation-specific models internally, but the
contract boundary is:

```text
Identification + Credential -> Identity
```

A source provider may resolve candidates and verify credentials internally.
Those internal steps must still end at canonical `Identity`.

The source provider must not know which target mapper will receive the
identity.

## Target Mapper Contract

A target identity mapper receives:

- canonical `Identity`
- target request

It produces:

- `TargetIdentity`

The target mapper does not receive:

- source credential values
- source provider results
- source implementation models
- authentication sessions
- transport payloads

The target mapper must not validate, authenticate, authorize, persist, bind,
issue tokens, issue assertions, perform network calls, or confirm target
account existence.

Its responsibility is projection only:

```text
Identity -> TargetIdentity
```

## Mapping Rules

Implementations are never mapped to each other directly.

Wrong:

```text
Kerberos -> LDAP
OAuth    -> Windows
SAML     -> API Key
```

Correct:

```text
Kerberos -> Identity -> LDAP TargetIdentity
OAuth    -> Identity -> Windows TargetIdentity
SAML     -> Identity -> API Key TargetIdentity
```

This keeps the model linear:

```text
Sources -> Identity -> Targets
```

instead of explosive:

```text
Sources x Targets
```

## Compatibility Rules

Adding a new source provider must not require changing:

- canonical `Identity`
- target identity mappers
- source providers that already exist

Adding a new target identity mapper must not require changing:

- canonical `Identity`
- source providers
- target identity mappers that already exist

Adding a new source or target must not require changing the core domain model.

## Identity Invariants

The protocol depends on these invariants:

1. `Identification` is not `Identity`.
2. `Credential` is not persisted by IdentityMapper.
3. `IdentityCandidate` is not the final domain identity.
4. `Identity` is produced only after successful verification.
5. `TargetIdentity` is a projection, not a second source of truth.
6. Source and target implementations never communicate directly.
7. Target mappers receive only canonical `Identity` and target request.

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

## Reference Implementation

This repository is the Python reference implementation of the draft protocol.

The protocol should be understandable without Python-specific details. A
separate implementation in another language should preserve the same
boundaries:

```text
Source Provider -> canonical Identity -> Target Identity Mapper
```

## Non-Goals

IdentityMapper must not become:

- credential manager
- identity store
- session manager
- authorization engine
- target system client
- LDAP wrapper
- OAuth wrapper
- authentication server

Its responsibility is the protocol boundary:

```text
proof -> Identity -> TargetIdentity
```

