# IdentityMapper

IdentityMapper defines a minimal identity abstraction and serves as a reference
implementation of the Invariant Mapping Pattern.

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

IdentityMapper defines the identity domain model and the contracts required to
authenticate it. It does not perform authentication itself.

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

`Identification` is not `Identity`.

```text
Identification
--------------
identifier = "meri"

Credential
----------
type = "opaque"
value = "..."

Authenticate
------------
verification

Verified Identity
-----------------
id = "42"
display_name = "Radomir Merhaut"
roles = [...]
claims = {...}
attributes = {...}
```

Most authentication systems can be described as two internal operations:

```text
Authenticate
    |
    +-- ResolveIdentity(identification)
    |
    +-- VerifyCredential(candidate, credential)
```

`Authenticate` is the orchestration. `ResolveIdentity` finds the identity
candidate. `VerifyCredential` proves that the credential belongs to that
candidate. Only then does the system produce a verified `Identity`.

An `IdentityCandidate` is not the domain invariant. It represents an
implementation candidate found during resolution:

```text
IdentityCandidate
-----------------
implementation_id = "candidate-42"
identification = Identification(...)
attributes = {...}
```

The verified `Identity.id` is the domain identifier. The candidate's
`implementation_id` is allowed to remain implementation-shaped.

Incorrect:

```text
implementation A -> implementation B
```

Correct:

```text
implementation A -> Identity -> implementation B
```

This keeps implementation details isolated and lets all integrations communicate
through a stable domain invariant.

## Project Scope

IdentityMapper focuses on identity:

- defining `Identification` as the claim used to select an identity candidate
- defining `Credential` as the material used to verify that claim
- defining `Identity` as the verified domain result
- making authentication explicit as identification plus verification
- keeping identity capabilities independent from implementation details

## Project Shape

```text
project:
  IdentityMapper

pattern:
  Invariant Mapping Pattern

core invariant:
  Identity

identification:
  Identification

candidate:
  IdentityCandidate

credential:
  Credential

capabilities:
  Authenticate
  ResolveIdentity
  VerifyCredential
```

## Status

Early project skeleton.
