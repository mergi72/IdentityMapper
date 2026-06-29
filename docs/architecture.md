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
       |
       v
Host
```

## Roles

`Implementation` is an external model, protocol, product, API, or
provider-specific representation.

In this repository, provider-specific code lives under
`identity_mapper.providers`.

Provider-specific reduction matrices live next to their provider code as
`matrix.json`.

A provider matrix is the provider footprint in the domain invariant. It is not
an authentication algorithm. It documents where the invariant points are found
in the provider world.

`Mapper` translates an implementation model into a domain model. It does not
validate, authenticate, authorize, persist, or decide.

`Domain Invariant` is the stable model that survives implementation changes.
In this project, the invariant is identity. `Identity` is the canonical model
shared by all source providers and target mappers.

`Capability` describes what can be done with the invariant without coupling
business logic to a specific implementation.

`Host` exposes one or more capabilities through a transport such as CLI, REST,
gRPC, or a message bus. A host is not part of the domain.

`Capability Protocol` defines request and response contracts for capabilities.
Hosts translate transport requests into capability requests and translate
capability responses back into transport responses.

## Rules

Implementations are never mapped to each other.

Every implementation maps only to the domain invariant.

Source providers and target mappers never communicate directly.

Mappers never contain business logic.

A mapper is deterministic. The same input always produces the same domain
model.

Business logic depends on the invariant, not on the implementation.

Hosts expose capabilities. They do not define the domain invariant.

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

## Source To Target Flow

IdentityMapper maps between identity worlds only through the canonical
`Identity` model.

```text
Source World
        |
        | proof / assertion
        v
Source Provider Capability
        |
        v
Identity (canonical model)
        |
        v
Target Mapper Capability
        |
        v
TargetIdentity (target projection)
        |
        v
Target World
```

The source world does not know the target world. The target world does not know
the source world.

This is not:

```text
Kerberos -> AD
```

It is:

```text
Kerberos proof -> Identity -> AD projection
```

`TargetIdentity` is not a second source of truth. It is the target-specific
projection of a verified `Identity`.

The target mapper must not validate, authenticate, authorize, persist, or
confirm account existence in the target system. It only translates the
canonical identity into the target shape.
