# IdentityMapper Documentation

IdentityMapper documents and tests the Invariant Mapping Pattern for the
identity domain.

## Documents

- [Architecture](architecture.md)
- [Host](host.md)
- [Host service](host-service.md)
- [Capability protocol](capability-protocol.md)
- [IdentityMapper protocol](identitymapper-protocol.md)
- [Compliance badge](compliance-badge.md)
- [RFCs](rfcs/index.md)
- [RFC 0001: IdentityMapper Protocol](rfcs/0001-identitymapper-protocol.md)
- [RFC 0002: IdentityMapper Compliance Suite](rfcs/0002-compliance-suite.md)
- [RFC 0003: IdentityMapper Protocol Versioning](rfcs/0003-protocol-versioning.md)
- [Compatibility matrix](compatibility-matrix.md)
- [Reduction matrix](reduction-matrix.md)
- [Reduction template](reduction-template.md)
- [Provider footprint](provider-footprint.md)
- [Architecture verification](architecture-verification.md)
- [Domain](domain/index.md)
- [Capabilities](capabilities/index.md)
- [Providers](providers/index.md)
- [MapIdentity](capabilities/map-identity.md)

## Rule

The reduction matrix describes the mapping. A provider matrix is the provider
footprint in the domain invariant.

```text
Implementation Model
        |
        v
Reduction Matrix
        |
        v
Provider Footprint
        |
        v
Domain Invariant
```

The mapper code is still the implementation. The matrix is the architectural
description of the reduction. It says where invariant points live in the
provider world.
