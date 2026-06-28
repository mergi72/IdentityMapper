# Architecture

IdentityMapper is built around one architectural idea: implementation models
must be reduced to a stable domain invariant before business logic depends on
them.

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

## Roles

`Implementation` is an external model, protocol, product, API, or
provider-specific representation.

`Mapper` translates an implementation model into a domain model. It does not
validate, authenticate, authorize, persist, or decide.

`Domain Invariant` is the stable model that survives implementation changes.
In this project, the invariant is identity.

`Capability` describes what can be done with the invariant without coupling
business logic to a specific implementation.

## Rules

Implementations are never mapped to each other.

Every implementation maps only to the domain invariant.

Mappers never contain business logic.

A mapper is deterministic. The same input always produces the same domain
model.

Business logic depends on the invariant, not on the implementation.

## Why

Without a domain invariant, every implementation must know every other
implementation.

```text
implementation A <-> implementation B
implementation A <-> implementation C
implementation B <-> implementation C
...
```

N implementations require N x (N - 1) direct mappings.

With a domain invariant, every implementation maps only once.

```text
implementation A --+
implementation B --+--> Domain Invariant
implementation C --+
...
```

N implementations require N mappings.

## Identity Flow

```text
Identification
        +
Credential
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

`Identification` is not `Identity`.

`IdentityCandidate` is not the domain invariant. It represents an implementation
candidate found during resolution.

The verified `Identity.id` is the domain identifier. The candidate's
`implementation_id` is allowed to remain implementation-shaped.
