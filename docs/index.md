# IdentityMapper Documentation

IdentityMapper documents and tests the Invariant Mapping Pattern for the
identity domain.

## Documents

- [Architecture](architecture.md)
- [Reduction matrix](reduction-matrix.md)
- [Architecture verification](architecture-verification.md)
- [Domain](domain/index.md)
- [Capabilities](capabilities/index.md)
- [Implementations](implementations/index.md)

## Rule

The reduction matrix describes the mapping. It does not execute it.

```text
Implementation Model
        |
        v
Reduction Matrix
        |
        v
Domain Invariant
```

The mapper code is still the implementation. The matrix is the architectural
description of the reduction.
