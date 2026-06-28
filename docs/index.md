# IdentityMapper Documentation

IdentityMapper documents and tests the Invariant Mapping Pattern for the
identity domain.

## Documents

- [Architecture](architecture.md)
- [Host](host.md)
- [Host service](host-service.md)
- [Reduction matrix](reduction-matrix.md)
- [Reduction template](reduction-template.md)
- [Provider footprint](provider-footprint.md)
- [Architecture verification](architecture-verification.md)
- [Domain](domain/index.md)
- [Capabilities](capabilities/index.md)
- [Providers](providers/index.md)

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
