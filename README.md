# IdentityMapper

IdentityMapper is the reference implementation of the Invariant Mapping Pattern
for the identity domain.

## The IdentityMapper Rule

Implementations are never mapped to each other.

Every implementation maps only to the domain invariant.

## The Mapper Rule

Mappers never contain business logic.

Their only responsibility is translating implementation models into domain
models.

A mapper does not validate, authenticate, authorize, persist, or decide.

A mapper is deterministic. The same input always produces the same domain
model.

IdentityMapper defines the identity domain model and the capabilities required
to authenticate an identity. It does not perform authentication itself.

## Core Idea

External systems, protocols, products, and APIs have their own implementation
models. A mapper translates one implementation model into a stable domain model.
Business logic works with the domain invariant, not with the implementation.

The Invariant Mapping Pattern is:

```text
Implementation
       |
       v
Mapper
       |
       v
Domain Invariant
       |
       v
Capabilities
```

The pattern can be summarized as:

1. Find the domain invariant.
2. Define the minimal domain contract.
3. Map every implementation to the invariant.
4. Business logic depends only on the invariant.
5. Capabilities extend the invariant.
6. Implementations never communicate directly.

## Quick Example

```text
Identification
--------------
identifier

Credential
----------
credential

        |
        v

Authenticate
    |
    +-- ResolveIdentity
    |
    +-- VerifyCredential

        |
        v

Identity
```

`Identification` is not `Identity`. Identification selects a candidate.
Credential verifies the candidate. Only successful authentication produces an
`Identity`.

## Documentation

The implementation details are intentionally kept out of this README.

- [Documentation index](docs/index.md)
- [Architecture](docs/architecture.md)
- [Architecture verification](docs/architecture-verification.md)
- [Reduction matrix](docs/reduction-matrix.md)
- [Reduction template](docs/reduction-template.md)
- [Domain concepts](docs/domain/index.md)
- [Capabilities](docs/capabilities/index.md)
- [Provider notes](docs/providers/index.md)

## Repository Structure

```text
src/identity_mapper/
  domain.py
  capabilities.py
  mapper.py
  providers/
    basic/
    ldap/
    oauth/
    ...

docs/
  architecture.md
  reduction-matrix.md
  reduction-template.md
  architecture-verification.md
  domain/
  capabilities/
  providers/
```

## Status

Reference implementation of the Invariant Mapping Pattern under active
development.
