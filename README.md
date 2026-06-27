# IdentityMapper

IdentityMapper defines a minimal identity abstraction and serves as a reference
implementation of the Invariant Mapping Pattern.

## The IdentityMapper Rule

Implementations are never mapped to each other.

Every implementation maps only to the domain invariant.

> IdentityMapper does not log a system in. IdentityMapper converts identity
> implementations into one shared domain invariant.

IdentityMapper does not authenticate users. It defines the domain model of
identity and the contracts required to authenticate it.

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
