# Changelog

All notable changes to IdentityMapper are documented here.

## v0.24.0

Host Service CLI and hardening checkpoint.

- Added `python -m identity_mapper_service authenticate`.
- Added text and JSON output for CLI authenticate.
- Documented `AuthenticationRejected` host conversion to `AuthenticateResponse(authenticated=False)`.
- Added HTTP request body size limiting with `max_request_body_bytes`.
- Added `413 payload_too_large` responses for oversized JSON requests.
- Added `authenticate_log_max_entries` and audit log trimming.
- Added config validation for port and positive integer limits.
- Added CLI override validation for service limits.
- Tests: 244 passed.

## v0.22.10

Authentication rejection protocol patch.

- Added `AuthenticationRejected` as the explicit capability protocol signal for rejected authentication.
- Made provider-specific authentication errors inherit from `AuthenticationRejected`.
- Updated Host Service to catch `AuthenticationRejected` instead of broad `ValueError`.
- Added coverage to ensure unexpected `ValueError` is not treated as authentication rejection.
- Tests: 234 passed.

## v0.22.9

Capability protocol terminology patch.

- Added `identity_mapper.capability_protocol` as the primary module for capability request and response contracts.
- Kept `identity_mapper.requests` and `identity_mapper.responses` as compatibility import surfaces.
- Updated Host Service imports to use the capability protocol module.
- Documented the primary capability protocol module.
- Tests: 232 passed.

## v0.22.8

Host Service response object patch.

- Added `HealthResponse`, `ProvidersResponse`, and `AuditResponse`.
- Made Host Service health, provider listing, and audit surfaces return response objects.
- Kept HTTP serialization in the HTTP adapter schema mapping layer.
- Added response mapping coverage for Host Service surfaces.
- Tests: 232 passed.

## v0.22.7

Authenticate response serialization patch.

- Included `AuthenticateResponse.error` in HTTP JSON response mapping.
- Added coverage for rejected authenticate response serialization.
- Confirmed successful HTTP authenticate responses include `error: null`.
- Tests: 231 passed.

## v0.22.6

Host Service capability protocol boundary patch.

- Removed transport-shaped authenticate payload handling from the Host Service.
- Kept HTTP JSON mapping inside the HTTP adapter.
- Made `authenticate_request()` the Host Service authenticate API.
- Updated tests to verify the service through capability requests.
- Tests: 230 passed.

## v0.22.5

Host Service operations patch.

- Added `request_id` to authenticate audit log entries.
- Added `duration_ms` to authenticate audit log entries.
- Added `python -m identity_mapper_service providers`.
- Added `python -m identity_mapper_service logs`.
- Added text, JSON, and HTML log output selection for CLI log reads.
- Tests: 230 passed.

## v0.22.4

Host Service audit log configuration patch.

- Added `authenticate_log_enabled` to `config/config.json`.
- Added `--disable-authenticate-log` for one-off service runs.
- Allowed Host Service to run without creating an authenticate request log.
- Kept audit endpoints available with an empty view when logging is disabled.
- Tests: 228 passed.

## v0.22.3

Host Service stabilization patch.

- Cleaned up Host Service response metadata.
- Removed duplicate audit log refresh behavior.
- Added `/audit` as an alias for authenticate audit logs.
- Added capability request and response contracts.
- Routed HTTP authenticate payloads through `AuthenticateRequest`.
- Wrote audit timestamps using the local timezone of the service machine.
- Rendered newest audit entries first in the browser view.
- Tests: 226 passed.

## v0.22.2

Host Service audit log presentation patch.

- Changed `GET /authenticate_logs` to render a browser-friendly HTML table.
- Added `GET /authenticate_logs?format=json` for API consumers.
- Added `GET /authenticate_logs?format=text` for terminal-style output.
- Kept browser auto-refresh for the audit log view.
- Confirmed credential values remain excluded from audit log output.

## v0.22.1

Host Service request log patch.

- Added metadata-only authenticate request logging.
- Added `GET /authenticate_logs`.
- Added `authenticate_log` to `config/config.json`.
- Added `python -m identity_mapper_service status`.
- Confirmed credential values are not written to the request log.

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
