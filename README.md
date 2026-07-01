# IdentityMapper

[![CI](https://github.com/mergi72/IdentityMapper/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mergi72/IdentityMapper/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/mergi72/IdentityMapper)](https://github.com/mergi72/IdentityMapper/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

IdentityMapper Protocol defines a canonical identity exchange between
heterogeneous identity systems. It does not replace authentication or trust. It
standardizes how verified identity is represented, projected, and resolved
across different identity worlds.

It is not an LDAP wrapper, OAuth wrapper, or authentication server.

It defines a shared boundary between identity worlds:

```text
Source Provider
    |
    v
canonical Identity
    |
    v
Target Identity Mapper
```

`Identity` is the canonical representation shared by all source providers and
target identity mappers.

## Project Status

IdentityMapper is a reference architecture under active development.

The core architecture has been validated against multiple identity models.

The reference implementation verifies:

```text
14 source providers x 14 target identity mappers = 196 projections
```

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

IdentityMapper defines the identity domain model, the capability contracts, and
the source-to-target identity protocol. It does not perform authentication as a
service by itself.

## Core Idea

External systems, protocols, products, and APIs have their own implementation
models. A mapper translates one implementation model into a stable domain model.
Business logic works with the domain invariant, not with the implementation.

Source providers reduce proof or assertions into the canonical `Identity`
model. Target mappers project that `Identity` into a target world. Source and
target implementations never communicate directly.

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
- [RFC 0001: IdentityMapper Protocol](docs/rfcs/0001-identitymapper-protocol.md)
- [Architecture](docs/architecture.md)
- [Architecture verification](docs/architecture-verification.md)
- [Capability protocol](docs/capability-protocol.md)
- [IdentityMapper protocol](docs/identitymapper-protocol.md)
- [Compatibility matrix](docs/compatibility-matrix.md)
- [Host](docs/host.md)
- [Host service](docs/host-service.md)
- [MapIdentity](docs/capabilities/map-identity.md)
- [Reduction matrix](docs/reduction-matrix.md)
- [Reduction template](docs/reduction-template.md)
- [Provider footprint](docs/provider-footprint.md)
- [Domain concepts](docs/domain/index.md)
- [Capabilities](docs/capabilities/index.md)
- [Provider notes](docs/providers/index.md)
- [Changelog](CHANGELOG.md)

## Repository Structure

```text
src/identity_mapper/
  domain.py
  capabilities.py
  capability_protocol.py
  mapper.py
  matrix.py
  providers/
    basic/
      matrix.json
    ldap/
      matrix.json
    oauth/
      matrix.json
    ...

src/identity_mapper_service/
  app.py
  registry.py
  responses.py
  schemas.py
  service.py

compliance/
  test_protocol_compliance.py

config/
  config.json

docs/
  rfcs/
  architecture.md
  compatibility-matrix.md
  identitymapper-protocol.md
  provider-footprint.md
  host.md
  host-service.md
  reduction-matrix.md
  reduction-template.md
  architecture-verification.md
  domain/
  capabilities/
  providers/
```

