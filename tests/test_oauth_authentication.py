import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.providers.oauth import (
    InMemoryOAuthTokenStore,
    OAuthAuthenticationError,
    OAuthAuthenticator,
    OAuthCredentialVerifier,
    OAuthIdentityResolver,
    OAuthTokenMapper,
    OAuthTokenRecord,
    OAuthTokenRequest,
)


def make_store() -> InMemoryOAuthTokenStore:
    return InMemoryOAuthTokenStore(
        [
            OAuthTokenRecord(
                token_id="oauth:token-1",
                subject="subject",
                access_token="accepted-token",
                identity_id="identity-oauth-1",
                display_name="Example Subject",
                email="subject@example.org",
                scopes=("read", "write"),
                claims={"issuer": "example-idp"},
                attributes={"source": "oauth"},
            ),
            OAuthTokenRecord(
                token_id="oauth:inactive",
                subject="inactive",
                access_token="inactive-token",
                identity_id="identity-inactive",
                active=False,
            ),
        ]
    )


def test_valid_oauth_token_returns_identity() -> None:
    identification, credential = OAuthTokenMapper().to_domain(
        OAuthTokenRequest(
            subject="subject",
            access_token="accepted-token",
            issuer="example-idp",
            audience="example-api",
        )
    )

    identity = OAuthAuthenticator(make_store()).authenticate(
        identification,
        credential,
    )

    assert identity == Identity(
        id="identity-oauth-1",
        display_name="Example Subject",
        email="subject@example.org",
        roles=("read", "write"),
        claims={"issuer": "example-idp"},
        attributes={"source": "oauth"},
    )


def test_invalid_oauth_token_raises_authentication_failure() -> None:
    identification, credential = OAuthTokenMapper().to_domain(
        OAuthTokenRequest(
            subject="subject",
            access_token="wrong-token",
        )
    )

    with pytest.raises(OAuthAuthenticationError):
        OAuthAuthenticator(make_store()).authenticate(
            identification,
            credential,
        )


def test_unknown_oauth_subject_resolves_to_none() -> None:
    candidate = OAuthIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="missing")
    )

    assert candidate is None


def test_inactive_oauth_token_resolves_to_none() -> None:
    candidate = OAuthIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="inactive")
    )

    assert candidate is None


def test_oauth_resolver_returns_candidate_not_identity() -> None:
    candidate = OAuthIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="subject")
    )

    assert candidate == IdentityCandidate(
        implementation_id="oauth:token-1",
        identification=Identification(identifier="subject"),
        attributes={"source": "oauth"},
    )


def test_oauth_verifier_checks_candidate_and_credential() -> None:
    candidate = IdentityCandidate(
        implementation_id="oauth:token-1",
        identification=Identification(identifier="subject"),
    )

    assert OAuthCredentialVerifier(make_store()).verify_credential(
        candidate,
        Credential(type="BEARER_TOKEN", value="accepted-token"),
    )


def test_oauth_mapper_contains_no_auth_logic() -> None:
    mapper = OAuthTokenMapper()

    known = mapper.to_domain(
        OAuthTokenRequest(subject="subject", access_token="accepted-token")
    )
    unknown = mapper.to_domain(
        OAuthTokenRequest(subject="missing", access_token="wrong-token")
    )

    assert known == (
        Identification(identifier="subject"),
        Credential(type="BEARER_TOKEN", value="accepted-token"),
    )
    assert unknown == (
        Identification(identifier="missing"),
        Credential(type="BEARER_TOKEN", value="wrong-token"),
    )
