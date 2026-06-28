# Host

A host exposes one or more capabilities through a transport.

Examples of host transports include:

- CLI
- REST
- gRPC
- Message Bus

A host is not part of the domain.

## Role

The domain defines the invariant.

Providers implement capabilities for a provider world.

Hosts expose those capabilities to the outside world.

```text
Transport
    |
    v
Host
    |
    v
Capability
    |
    v
Provider
    |
    v
Domain Invariant
```

## Boundary

A host should not introduce identity concepts.

It should not turn IdentityMapper into an auth server, session manager, token
issuer, authorization system, or user database.

It only exposes existing capabilities.

For example, a minimal REST host may expose:

```text
POST /authenticate
POST /resolve-identity
POST /verify-credential
```

The host receives transport-shaped input, selects a provider, calls a
capability, and returns a transport-shaped response.

## First Runtime Step

The first runtime should be small.

A CLI host is a better first host than a server:

```text
identity-mapper check
identity-mapper authenticate --provider basic
```

The goal is to prove that capabilities can be hosted without changing the core
domain model, provider contracts, or mapper rules.
