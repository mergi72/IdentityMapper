import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
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
