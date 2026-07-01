# Changelog

All notable changes to IdentityMapper are documented here.

## v0.33.0

Demo Host Service target mapper wiring checkpoint.

- Registered `basic` and `windows` target identity mappers in the
  `--demo-basic` runtime registry.
- Verified the lab flow:
  `basic proof -> canonical Identity -> basic/windows TargetIdentity`.
- Kept the fix in runtime demo wiring only; no core domain, capability
  protocol, provider, or target mapper contract changes were required.
- Stabilized HTTP `413 payload_too_large` responses on Windows by draining
  small rejected request bodies before closing the connection.
- Tests: 724 passed.

## v0.32.1

Protocol specification documentation patch.

- Expanded `docs/identitymapper-protocol.md` into `IdentityMapper Protocol 1.0
  Draft`.
- Added source provider contract, target mapper contract, mapping rules,
  compatibility rules, identity invariants, and non-goals.
- Added `docs/compatibility-matrix.md` with the verified `14 x 14` projection
  coverage.
- Updated the README to state the protocol boundary and distinguish
  IdentityMapper from LDAP wrappers, OAuth wrappers, and authentication
  servers.
- Tests: 723 passed.

## v0.32.0

IdentityMapper Protocol design principles checkpoint.

- Added `docs/identitymapper-protocol.md`.
- Documented IdentityMapper as a protocol for translating identity proofs into
  canonical `Identity` and projecting that identity into target worlds.
- Documented the source/target boundary:
  `Source Provider -> canonical Identity -> Target Identity Mapper`.
- Clarified that IdentityMapper is not a formal standard, credential manager,
  identity store, session manager, authorization engine, or target system
  client.
- Linked the protocol document from the README and documentation index.
- Tests: 723 passed.

## v0.31.2

All-to-all projection verification patch.

- Added an explicit all-to-all projection coverage guard for every source
  provider and every target identity mapper.
- Refactored projection tests around `assert_source_can_project_to_target()`.
- Verified the direct boundary: source provider produces canonical `Identity`;
  target mapper projects only that `Identity` and target request.
- Documented the all-to-all projection guarantee in architecture verification.
- Tests: 723 passed.

## v0.31.1

Target mapper terminology patch.

- Replaced target-side `target_provider` terminology with `target_mapper`.
- Added `UnknownTargetMapperError` for missing target mapper requests.
- Kept source-side provider terminology unchanged.
- Updated audit output to use `target_mapper`.
- Updated Host Service docs to distinguish source provider capabilities from
  target mapper capabilities.
- Tests: 716 passed.

## v0.31.0

Full provider target projection checkpoint.

- Added target projection mappers for the remaining provider worlds in this
  repository: BasicAuth, API Key, Client Certificate / mTLS, OAuth, WebAuthn /
  FIDO2, Passkeys, MFA, Federated Identity, and Guest / Anonymous Identity.
- Kept every target mapper projection-only: no credential values, no token
  values, no session tokens, no assertion values, no proof values, no runtime
  connection objects, and no target existence confirmation.
- Exported the new target projection mappers from their provider packages.
- Expanded the provider capability contract suite to verify every included
  source provider can map through canonical `Identity` to every included target
  provider projection.
- Documented the full verified target projection suite.
- Tests: 715 passed.

## v0.30.0

Target projection verification checkpoint.

- Added LDAP, Kerberos, JWT, and SAML target projection mappers.
- Kept all target mappers projection-only: no lookup, bind, token issuance,
  assertion issuance, network call, or target existence confirmation.
- Exported the new target projection mappers from their provider packages.
- Added provider tests for each new target projection.
- Added contract coverage proving every included source provider can map
  through canonical `Identity` to Windows / AD, LDAP, Kerberos, JWT, and SAML
  target projections.
- Documented the verified target projection suite.
- Tests: 589 passed.

## v0.29.1

Canonical identity documentation patch.

- Documented `Identity` as the canonical representation shared by source
  providers and target mappers.
- Documented the source-to-target flow as `source proof -> Identity ->
  TargetIdentity`.
- Added docs for `MapIdentity`, `IdentityTarget`, and `TargetIdentity`.
- Documented `POST /map-identity` in the Host Service docs.
- Clarified that target mappers receive the verified canonical `Identity`, not
  source credential values.
- Tests: 503 passed.

## v0.29.0

Windows / AD target projection checkpoint.

- Added `WindowsAdTargetIdentityMapper` for projecting a verified `Identity` into an AD target shape.
- Added `WindowsAdTargetProjectionConfig`.
- Added AD projection attributes: `upn_candidate`, `sam_account_name_candidate`, `mail_hint`, and `group_hints`.
- Verified every existing source provider can map through `Identity` to the Windows / AD target projection.
- Kept the mapper projection-only: no AD bind, no LDAP lookup, no network call, no service account, and no account existence confirmation.
- Tests: 503 passed.

## v0.28.1

Provider mapping contract checkpoint.

- Added provider x provider identity mapping contract coverage.
- Verified every source provider can map to every target provider through a verified `Identity`.
- Verified each provider can map to itself.
- Verified target mapping is not called when source identity proof is rejected.
- Tests: 484 passed.

## v0.28.0

Identity mapping checkpoint.

- Added `IdentityTarget` and `TargetIdentity` domain models for target identity worlds.
- Added the `MapIdentity` capability.
- Added `MapIdentityRequest` and `MapIdentityResponse` to the capability protocol.
- Added Host Service support for mapping source identity proof to target identity context.
- Added HTTP `POST /map-identity`.
- Added target provider audit metadata for identity mapping invocations.
- Enforced that target mapping runs only after source proof produces a verified `Identity`.
- Added coverage for mapping one source identity proof to another target and to itself.
- Tests: 274 passed.

## v0.27.1

Capability invocation log naming patch.

- Renamed the primary Host Service audit writer from `RequestLog` to `CapabilityInvocationLog`.
- Kept `RequestLog` as a compatibility alias.
- Updated Host Service wiring and tests to use the current capability invocation terminology.
- Tests: 266 passed.

## v0.27.0

Capability Invocation Log checkpoint.

- Generalized the request log into a capability invocation log.
- Added `capability` to audit entries for `authenticate`, `resolve_identity`, and `verify_credential`.
- Added audit metadata for `candidate_id` and `verified`.
- Made `/audit` the primary capability audit endpoint.
- Kept `/authenticate_logs` as a compatibility alias.
- Renamed config keys to `audit_log_enabled`, `audit_log`, and `audit_log_max_entries`.
- Kept legacy `authenticate_log_*` config keys and CLI flags as compatibility fallbacks.
- Tests: 266 passed.

## v0.26.0

Host API completion checkpoint.

- Added HTTP `POST /resolve-identity`.
- Added HTTP `POST /verify-credential`.
- Added Host Service request handling for `ResolveIdentityRequest` and `VerifyCredentialRequest`.
- Added provider registry support for resolvers and credential verifiers.
- Made `ResolveIdentityRequest.provider` and `VerifyCredentialRequest.provider` optional.
- Added JSON mapping for `IdentityCandidate`.
- Documented the Host Service as exposing all three core identity capabilities.
- Tests: 263 passed.

## v0.25.1

Release archive hygiene patch.

- Added `.gitattributes` export rules for Python caches and local runtime artifacts.
- Kept ignored build, cache, virtual environment, and log files out of source archives.
- Confirmed the working tree is clean after local cache cleanup.
- Tests: 250 passed.

## v0.25.0

Provider selection checkpoint.

- Made `AuthenticateRequest.provider` optional.
- Added host-driven provider selection for authenticate requests.
- Kept explicit provider routing available for callers that need it.
- Logged the selected provider for implicit authenticate requests.
- Allowed HTTP and CLI authenticate requests to omit `provider`.
- Documented provider as a host routing hint, not a domain concept.
- Tests: 250 passed.

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
