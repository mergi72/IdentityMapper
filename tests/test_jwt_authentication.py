import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
    IdentityTarget,
    TargetIdentity,
)
from identity_mapper.providers.jwt import (
    InMemoryJwtStore,
    JwtAuthenticationError,
    JwtAuthenticator,
    JwtCredentialVerifier,
    JwtIdentityResolver,
    JwtMapper,
    JwtRecord,
    JwtRequest,
    JwtTargetIdentityMapper,
    JwtTargetProjectionConfig,
)


def make_store() -> InMemoryJwtStore:
    return InMemoryJwtStore(
        [
            JwtRecord(
                jwt_id="jwt:token-1",
                subject="subject",
                bearer_token="accepted-bearer-token",
                identity_id="identity-jwt-1",
                issuer="example-issuer",
                audience="example-api",
                display_name="Example Subject",
                email="subject@example.org",
                roles=("read", "write"),
                claims={"scope": "read write"},
                attributes={"source": "jwt"},
            ),
            JwtRecord(
                jwt_id="jwt:inactive",
                subject="inactive",
                bearer_token="inactive-bearer-token",
                identity_id="identity-inactive-jwt",
                active=False,
            ),
        ]
    )


def test_valid_jwt_bearer_token_returns_identity() -> None:
    identification, credential = JwtMapper().to_domain(
        JwtRequest(
            subject="subject",
            bearer_token="accepted-bearer-token",
            issuer="example-issuer",
            audience="example-api",
        )
    )

    identity = JwtAuthenticator(make_store()).authenticate(
        identification,
        credential,
    )

    assert identity == Identity(
        id="identity-jwt-1",
        display_name="Example Subject",
        email="subject@example.org",
        roles=("read", "write"),
        claims={"scope": "read write"},
        attributes={"source": "jwt"},
    )


def test_invalid_jwt_bearer_token_raises_authentication_failure() -> None:
    identification, credential = JwtMapper().to_domain(
        JwtRequest(
            subject="subject",
            bearer_token="wrong-bearer-token",
        )
    )

    with pytest.raises(JwtAuthenticationError):
        JwtAuthenticator(make_store()).authenticate(
            identification,
            credential,
        )


def test_unknown_jwt_subject_resolves_to_none() -> None:
    candidate = JwtIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="missing")
    )

    assert candidate is None


def test_inactive_jwt_token_resolves_to_none() -> None:
    candidate = JwtIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="inactive")
    )

    assert candidate is None


def test_jwt_resolver_returns_candidate_not_identity() -> None:
    candidate = JwtIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="subject")
    )

    assert candidate == IdentityCandidate(
        implementation_id="jwt:token-1",
        identification=Identification(identifier="subject"),
        attributes={"source": "jwt"},
    )


def test_jwt_verifier_checks_candidate_and_credential() -> None:
    candidate = IdentityCandidate(
        implementation_id="jwt:token-1",
        identification=Identification(identifier="subject"),
    )

    assert JwtCredentialVerifier(make_store()).verify_credential(
        candidate,
        Credential(type="BEARER_TOKEN", value="accepted-bearer-token"),
    )


def test_jwt_mapper_contains_no_auth_logic() -> None:
    mapper = JwtMapper()

    known = mapper.to_domain(
        JwtRequest(
            subject="subject",
            bearer_token="accepted-bearer-token",
        )
    )
    unknown = mapper.to_domain(
        JwtRequest(
            subject="missing",
            bearer_token="wrong-bearer-token",
        )
    )

    assert known == (
        Identification(identifier="subject"),
        Credential(type="BEARER_TOKEN", value="accepted-bearer-token"),
    )
    assert unknown == (
        Identification(identifier="missing"),
        Credential(type="BEARER_TOKEN", value="wrong-bearer-token"),
    )


def test_jwt_target_mapper_projects_identity_to_jwt_shape() -> None:
    identity = Identity(
        id="subject",
        email="subject@example.org",
        roles=("read", "write"),
        claims={"scope": "read write"},
    )
    target = IdentityTarget(provider="jwt", realm="issuer", purpose="api")

    target_identity = JwtTargetIdentityMapper().map_identity(identity, target)

    assert target_identity == TargetIdentity(
        identifier="jwt:subject",
        target=target,
        attributes={
            "subject_candidate": "subject",
            "issuer_hint": "issuer",
            "audience_hint": "api",
            "email_hint": "subject@example.org",
            "claim_hints": {"scope": "read write"},
            "role_hints": ("read", "write"),
        },
    )


def test_jwt_target_mapper_can_use_default_issuer_and_audience() -> None:
    identity = Identity(id="subject")
    target = IdentityTarget(provider="jwt")

    target_identity = JwtTargetIdentityMapper(
        JwtTargetProjectionConfig(default_issuer="issuer", default_audience="api")
    ).map_identity(identity, target)

    assert target_identity is not None
    assert target_identity.attributes["issuer_hint"] == "issuer"
    assert target_identity.attributes["audience_hint"] == "api"


def test_jwt_target_mapper_does_not_issue_or_verify_token() -> None:
    identity = Identity(id="missing-token")
    target = IdentityTarget(provider="jwt", realm="issuer")

    target_identity = JwtTargetIdentityMapper().map_identity(identity, target)

    assert target_identity is not None
    assert target_identity.attributes["subject_candidate"] == "missing-token"
    assert "token" not in target_identity.attributes


def test_jwt_target_mapper_ignores_non_jwt_target() -> None:
    assert (
        JwtTargetIdentityMapper().map_identity(
            Identity(id="subject"),
            IdentityTarget(provider="saml"),
        )
        is None
    )
