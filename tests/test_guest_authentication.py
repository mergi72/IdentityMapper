import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper_guest import (
    GuestAuthenticationError,
    GuestAuthenticator,
    GuestCredentialVerifier,
    GuestIdentityResolver,
    GuestMapper,
    GuestRequest,
    GuestSessionRecord,
    InMemoryGuestSessionStore,
)


def make_store() -> InMemoryGuestSessionStore:
    return InMemoryGuestSessionStore(
        [
            GuestSessionRecord(
                session_id="guest-session-1",
                session_token="accepted-guest-token",
                identity_id="identity-guest-1",
                claims={"anonymous": True},
                attributes={"source": "guest"},
            ),
            GuestSessionRecord(
                session_id="inactive-guest-session",
                session_token="inactive-guest-token",
                identity_id="identity-inactive-guest",
                active=False,
            ),
        ]
    )


def test_valid_guest_session_returns_identity() -> None:
    identification, credential = GuestMapper().to_domain(
        GuestRequest(
            session_id="guest-session-1",
            session_token="accepted-guest-token",
        )
    )

    identity = GuestAuthenticator(make_store()).authenticate(
        identification,
        credential,
    )

    assert identity == Identity(
        id="identity-guest-1",
        display_name="Guest",
        roles=("guest",),
        claims={"anonymous": True},
        attributes={"source": "guest"},
    )


def test_invalid_guest_session_token_raises_authentication_failure() -> None:
    identification, credential = GuestMapper().to_domain(
        GuestRequest(
            session_id="guest-session-1",
            session_token="wrong-guest-token",
        )
    )

    with pytest.raises(GuestAuthenticationError):
        GuestAuthenticator(make_store()).authenticate(
            identification,
            credential,
        )


def test_unknown_guest_session_resolves_to_none() -> None:
    candidate = GuestIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="missing-guest-session")
    )

    assert candidate is None


def test_inactive_guest_session_resolves_to_none() -> None:
    candidate = GuestIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="inactive-guest-session")
    )

    assert candidate is None


def test_guest_resolver_returns_candidate_not_identity() -> None:
    candidate = GuestIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="guest-session-1", realm="guest")
    )

    assert candidate == IdentityCandidate(
        implementation_id="guest-session-1",
        identification=Identification(
            identifier="guest-session-1",
            realm="guest",
        ),
        attributes={"source": "guest"},
    )


def test_guest_verifier_checks_candidate_and_credential() -> None:
    candidate = IdentityCandidate(
        implementation_id="guest-session-1",
        identification=Identification(identifier="guest-session-1"),
    )

    assert GuestCredentialVerifier(make_store()).verify_credential(
        candidate,
        Credential(
            type="GUEST_SESSION",
            value="accepted-guest-token",
        ),
    )


def test_guest_mapper_contains_no_auth_logic() -> None:
    mapper = GuestMapper()

    known = mapper.to_domain(
        GuestRequest(
            session_id="guest-session-1",
            session_token="accepted-guest-token",
        )
    )
    unknown = mapper.to_domain(
        GuestRequest(
            session_id="missing-guest-session",
            session_token="wrong-guest-token",
        )
    )

    assert known == (
        Identification(
            identifier="guest-session-1",
            realm="guest",
            attributes={"kind": "guest"},
        ),
        Credential(
            type="GUEST_SESSION",
            value="accepted-guest-token",
        ),
    )
    assert unknown == (
        Identification(
            identifier="missing-guest-session",
            realm="guest",
            attributes={"kind": "guest"},
        ),
        Credential(
            type="GUEST_SESSION",
            value="wrong-guest-token",
        ),
    )
