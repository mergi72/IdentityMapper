# Changelog

All notable changes to IdentityMapper are documented here.

## v0.22.0

Host Service runtime prototype.

- Added `identity_mapper_service` as a minimal capability host.
- Added a provider registry for hosted authenticators.
- Added stdlib HTTP endpoints for `GET /health`, `GET /providers`, and
  `POST /authenticate`.
- Added `python -m identity_mapper_service serve`.
- Kept service responsibility limited to transport and lifecycle.

## v0.21.0

CI and release cleanup checkpoint.

- Added GitHub Actions CI for `main` and `develop`.
- Runs the provider capability contract suite on Python 3.11 and 3.12.
- Runs Python bytecode compilation for `src` and `tests`.
- Documented CI in architecture verification.

## v0.20.1

Architecture contract verification documentation patch.

- Promoted provider capability contract verification to its own documentation
  section.
- Clarified that the provider contract test is an architectural test.
- Confirmed the core domain model and capability contract remained unchanged.

## v0.20.0

Provider capability contract verification release.

- Added a shared provider capability contract test suite.
- Verified all providers through the same mapper, resolver, verifier, and
  authenticator flow.
- Confirmed resolvers return `IdentityCandidate`, not `Identity`.
- Confirmed invalid credentials are rejected consistently.

## v0.19.0

Provider Footprint documentation release.

- Introduced Provider Footprint as the meaning of provider-owned matrices.
- Added `docs/provider-footprint.md`.
- Clarified that `matrix.json` is not authentication logic.
- Kept `matrix.json` file names and `ReductionMatrix` API unchanged.

## v0.18.0

Reduction Template and provider-owned matrices.

- Moved provider packages under `identity_mapper.providers`.
- Added the root `ReductionMatrix` contract.
- Added compact provider-owned `matrix.json` files for all providers.
- Renamed implementation docs to provider docs.
- Kept core invariant and capability contracts unchanged.

## v0.1.0

Initial public architecture baseline.

- Established the core identity domain model.
- Defined identity capabilities.
- Added the generic Mapper abstraction.
- Introduced the Invariant Mapping Pattern.
