import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.providers.mfa import (
    InMemoryMfaStore,
    MfaAuthenticationError,
    MfaAuthenticator,
    MfaCredentialVerifier,
    MfaFactor,
    MfaIdentityResolver,
    MfaMapper,
    MfaRecord,
    MfaRequest,
)


def make_store() -> InMemoryMfaStore:
    return InMemoryMfaStore(
        [
            MfaRecord(
                implementation_id="mfa:subject",
                identifier="subject",
                required_factors={
                    "PASSWORD": "accepted-password",
                    "TOTP": "123456",
                },
                identity_id="identity-mfa-1",
                display_name="Example MFA Subject",
                email="subject@example.org",
                roles=("employee", "mfa"),
                claims={"assurance": "multi-factor"},
                attributes={"source": "mfa"},
            ),
            MfaRecord(
                implementation_id="mfa:inactive",
                identifier="inactive",
                required_factors={"PASSWORD": "inactive-password"},
                identity_id="identity-inactive-mfa",
                active=False,
            ),
        ]
    )


def valid_request() -> MfaRequest:
    return MfaRequest(
        identifier="subject",
        factors=(
            MfaFactor(type="PASSWORD", value="accepted-password"),
            MfaFactor(type="TOTP", value="123456"),
        ),
    )


def test_valid_mfa_factors_return_identity() -> None:
    identification, credential = MfaMapper().to_domain(valid_request())

    identity = MfaAuthenticator(make_store()).authenticate(
        identification,
        credential,
    )

    assert identity == Identity(
        id="identity-mfa-1",
        display_name="Example MFA Subject",
        email="subject@example.org",
        roles=("employee", "mfa"),
        claims={"assurance": "multi-factor"},
        attributes={"source": "mfa"},
    )


def test_missing_mfa_factor_raises_authentication_failure() -> None:
    identification, credential = MfaMapper().to_domain(
        MfaRequest(
            identifier="subject",
            factors=(
                MfaFactor(type="PASSWORD", value="accepted-password"),
            ),
        )
    )

    with pytest.raises(MfaAuthenticationError):
        MfaAuthenticator(make_store()).authenticate(
            identification,
            credential,
        )


def test_wrong_mfa_factor_raises_authentication_failure() -> None:
    identification, credential = MfaMapper().to_domain(
        MfaRequest(
            identifier="subject",
            factors=(
                MfaFactor(type="PASSWORD", value="accepted-password"),
                MfaFactor(type="TOTP", value="000000"),
            ),
        )
    )

    with pytest.raises(MfaAuthenticationError):
        MfaAuthenticator(make_store()).authenticate(
            identification,
            credential,
        )


def test_unknown_mfa_identifier_resolves_to_none() -> None:
    candidate = MfaIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="missing")
    )

    assert candidate is None


def test_inactive_mfa_identifier_resolves_to_none() -> None:
    candidate = MfaIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="inactive")
    )

    assert candidate is None


def test_mfa_resolver_returns_candidate_not_identity() -> None:
    candidate = MfaIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="subject")
    )

    assert candidate == IdentityCandidate(
        implementation_id="mfa:subject",
        identification=Identification(identifier="subject"),
        attributes={"source": "mfa"},
    )


def test_mfa_verifier_checks_candidate_and_credential() -> None:
    candidate = IdentityCandidate(
        implementation_id="mfa:subject",
        identification=Identification(identifier="subject"),
    )
    _, credential = MfaMapper().to_domain(valid_request())

    assert MfaCredentialVerifier(make_store()).verify_credential(
        candidate,
        credential,
    )


def test_mfa_mapper_contains_no_auth_logic() -> None:
    mapper = MfaMapper()

    known = mapper.to_domain(valid_request())
    unknown = mapper.to_domain(
        MfaRequest(
            identifier="missing",
            factors=(
                MfaFactor(type="PASSWORD", value="wrong-password"),
                MfaFactor(type="TOTP", value="000000"),
            ),
        )
    )

    assert known[0] == Identification(identifier="subject")
    assert known[1].type == "MFA_FACTORS"
    assert known[1].metadata == {"factor_count": 2}
    assert unknown[0] == Identification(identifier="missing")
    assert unknown[1].type == "MFA_FACTORS"
    assert unknown[1].metadata == {"factor_count": 2}
