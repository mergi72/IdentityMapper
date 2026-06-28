import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.providers.basic import (
    BasicAuthenticationError,
    BasicAuthenticationMapper,
    BasicAuthenticationRequest,
    BasicAuthenticator,
    BasicCredentialVerifier,
    BasicIdentityResolver,
    BasicUserRecord,
    InMemoryBasicUserStore,
)


def make_store() -> InMemoryBasicUserStore:
    return InMemoryBasicUserStore(
        [
            BasicUserRecord(
                implementation_id="basic:subject",
                username="subject",
                password="accepted",
                identity_id="identity-1",
                display_name="Example Subject",
                roles=("reader",),
                claims={"scope": "example"},
                attributes={"source": "basic"},
            )
        ]
    )


def test_valid_user_password_returns_identity() -> None:
    identification, credential = BasicAuthenticationMapper().to_domain(
        BasicAuthenticationRequest(
            username="subject",
            password="accepted",
        )
    )

    identity = BasicAuthenticator(make_store()).authenticate(
        identification,
        credential,
    )

    assert identity == Identity(
        id="identity-1",
        display_name="Example Subject",
        roles=("reader",),
        claims={"scope": "example"},
        attributes={"source": "basic"},
    )


def test_invalid_password_raises_authentication_failure() -> None:
    identification, credential = BasicAuthenticationMapper().to_domain(
        BasicAuthenticationRequest(
            username="subject",
            password="wrong",
        )
    )

    with pytest.raises(BasicAuthenticationError):
        BasicAuthenticator(make_store()).authenticate(
            identification,
            credential,
        )


def test_unknown_user_resolves_to_none() -> None:
    candidate = BasicIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="missing")
    )

    assert candidate is None


def test_basic_resolver_returns_candidate_not_identity() -> None:
    candidate = BasicIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="subject")
    )

    assert candidate == IdentityCandidate(
        implementation_id="basic:subject",
        identification=Identification(identifier="subject"),
        attributes={"source": "basic"},
    )


def test_basic_verifier_checks_candidate_and_credential() -> None:
    candidate = IdentityCandidate(
        implementation_id="basic:subject",
        identification=Identification(identifier="subject"),
    )

    assert BasicCredentialVerifier(make_store()).verify_credential(
        candidate,
        Credential(type="PASSWORD", value="accepted"),
    )


def test_basic_mapper_contains_no_auth_logic() -> None:
    mapper = BasicAuthenticationMapper()

    known = mapper.to_domain(
        BasicAuthenticationRequest(username="subject", password="accepted")
    )
    unknown = mapper.to_domain(
        BasicAuthenticationRequest(username="missing", password="wrong")
    )

    assert known == (
        Identification(identifier="subject"),
        Credential(type="PASSWORD", value="accepted"),
    )
    assert unknown == (
        Identification(identifier="missing"),
        Credential(type="PASSWORD", value="wrong"),
    )
