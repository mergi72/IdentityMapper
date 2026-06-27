import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper_webauthn import (
    InMemoryWebAuthnCredentialStore,
    WebAuthnAuthenticationError,
    WebAuthnAuthenticator,
    WebAuthnCredentialRecord,
    WebAuthnCredentialVerifier,
    WebAuthnIdentityResolver,
    WebAuthnMapper,
    WebAuthnRequest,
)


def make_store() -> InMemoryWebAuthnCredentialStore:
    return InMemoryWebAuthnCredentialStore(
        [
            WebAuthnCredentialRecord(
                credential_id="webauthn:credential-1",
                assertion="accepted-webauthn-assertion",
                identity_id="identity-webauthn-1",
                user_handle="user-handle-1",
                relying_party_id="example.org",
                display_name="Example WebAuthn Subject",
                email="subject@example.org",
                roles=("employee", "webauthn"),
                claims={"authenticator": "platform"},
                attributes={"source": "webauthn"},
            ),
            WebAuthnCredentialRecord(
                credential_id="webauthn:inactive",
                assertion="inactive-webauthn-assertion",
                identity_id="identity-inactive-webauthn",
                active=False,
            ),
        ]
    )


def test_valid_webauthn_assertion_returns_identity() -> None:
    identification, credential = WebAuthnMapper().to_domain(
        WebAuthnRequest(
            credential_id="webauthn:credential-1",
            assertion="accepted-webauthn-assertion",
            user_handle="user-handle-1",
            relying_party_id="example.org",
            challenge="challenge-1",
        )
    )

    identity = WebAuthnAuthenticator(make_store()).authenticate(
        identification,
        credential,
    )

    assert identity == Identity(
        id="identity-webauthn-1",
        display_name="Example WebAuthn Subject",
        email="subject@example.org",
        roles=("employee", "webauthn"),
        claims={"authenticator": "platform"},
        attributes={"source": "webauthn"},
    )


def test_invalid_webauthn_assertion_raises_authentication_failure() -> None:
    identification, credential = WebAuthnMapper().to_domain(
        WebAuthnRequest(
            credential_id="webauthn:credential-1",
            assertion="wrong-webauthn-assertion",
        )
    )

    with pytest.raises(WebAuthnAuthenticationError):
        WebAuthnAuthenticator(make_store()).authenticate(
            identification,
            credential,
        )


def test_unknown_webauthn_credential_resolves_to_none() -> None:
    candidate = WebAuthnIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="webauthn:missing")
    )

    assert candidate is None


def test_inactive_webauthn_credential_resolves_to_none() -> None:
    candidate = WebAuthnIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="webauthn:inactive")
    )

    assert candidate is None


def test_webauthn_resolver_returns_candidate_not_identity() -> None:
    candidate = WebAuthnIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="webauthn:credential-1")
    )

    assert candidate == IdentityCandidate(
        implementation_id="webauthn:credential-1",
        identification=Identification(identifier="webauthn:credential-1"),
        attributes={"source": "webauthn"},
    )


def test_webauthn_verifier_checks_candidate_and_credential() -> None:
    candidate = IdentityCandidate(
        implementation_id="webauthn:credential-1",
        identification=Identification(identifier="webauthn:credential-1"),
    )

    assert WebAuthnCredentialVerifier(make_store()).verify_credential(
        candidate,
        Credential(
            type="WEBAUTHN_ASSERTION",
            value="accepted-webauthn-assertion",
        ),
    )


def test_webauthn_mapper_contains_no_auth_logic() -> None:
    mapper = WebAuthnMapper()

    known = mapper.to_domain(
        WebAuthnRequest(
            credential_id="webauthn:credential-1",
            assertion="accepted-webauthn-assertion",
        )
    )
    unknown = mapper.to_domain(
        WebAuthnRequest(
            credential_id="webauthn:missing",
            assertion="wrong-webauthn-assertion",
        )
    )

    assert known == (
        Identification(identifier="webauthn:credential-1"),
        Credential(
            type="WEBAUTHN_ASSERTION",
            value="accepted-webauthn-assertion",
        ),
    )
    assert unknown == (
        Identification(identifier="webauthn:missing"),
        Credential(
            type="WEBAUTHN_ASSERTION",
            value="wrong-webauthn-assertion",
        ),
    )
