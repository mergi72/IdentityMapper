import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.providers.passkeys import (
    InMemoryPasskeyStore,
    PasskeyAuthenticationError,
    PasskeyAuthenticator,
    PasskeyCredentialVerifier,
    PasskeyIdentityResolver,
    PasskeyMapper,
    PasskeyRecord,
    PasskeyRequest,
)


def make_store() -> InMemoryPasskeyStore:
    return InMemoryPasskeyStore(
        [
            PasskeyRecord(
                passkey_id="passkey:credential-1",
                assertion="accepted-passkey-assertion",
                identity_id="identity-passkey-1",
                user_handle="user-handle-1",
                relying_party_id="example.org",
                device_name="Example Device",
                display_name="Example Passkey Subject",
                email="subject@example.org",
                roles=("employee", "passkey"),
                claims={"authenticator": "synced-passkey"},
                attributes={"source": "passkeys"},
            ),
            PasskeyRecord(
                passkey_id="passkey:inactive",
                assertion="inactive-passkey-assertion",
                identity_id="identity-inactive-passkey",
                active=False,
            ),
        ]
    )


def test_valid_passkey_assertion_returns_identity() -> None:
    identification, credential = PasskeyMapper().to_domain(
        PasskeyRequest(
            passkey_id="passkey:credential-1",
            assertion="accepted-passkey-assertion",
            user_handle="user-handle-1",
            relying_party_id="example.org",
            device_name="Example Device",
        )
    )

    identity = PasskeyAuthenticator(make_store()).authenticate(
        identification,
        credential,
    )

    assert identity == Identity(
        id="identity-passkey-1",
        display_name="Example Passkey Subject",
        email="subject@example.org",
        roles=("employee", "passkey"),
        claims={"authenticator": "synced-passkey"},
        attributes={"source": "passkeys"},
    )


def test_invalid_passkey_assertion_raises_authentication_failure() -> None:
    identification, credential = PasskeyMapper().to_domain(
        PasskeyRequest(
            passkey_id="passkey:credential-1",
            assertion="wrong-passkey-assertion",
        )
    )

    with pytest.raises(PasskeyAuthenticationError):
        PasskeyAuthenticator(make_store()).authenticate(
            identification,
            credential,
        )


def test_unknown_passkey_resolves_to_none() -> None:
    candidate = PasskeyIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="passkey:missing")
    )

    assert candidate is None


def test_inactive_passkey_resolves_to_none() -> None:
    candidate = PasskeyIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="passkey:inactive")
    )

    assert candidate is None


def test_passkey_resolver_returns_candidate_not_identity() -> None:
    candidate = PasskeyIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="passkey:credential-1")
    )

    assert candidate == IdentityCandidate(
        implementation_id="passkey:credential-1",
        identification=Identification(identifier="passkey:credential-1"),
        attributes={"source": "passkeys"},
    )


def test_passkey_verifier_checks_candidate_and_credential() -> None:
    candidate = IdentityCandidate(
        implementation_id="passkey:credential-1",
        identification=Identification(identifier="passkey:credential-1"),
    )

    assert PasskeyCredentialVerifier(make_store()).verify_credential(
        candidate,
        Credential(
            type="PASSKEY_ASSERTION",
            value="accepted-passkey-assertion",
        ),
    )


def test_passkey_mapper_contains_no_auth_logic() -> None:
    mapper = PasskeyMapper()

    known = mapper.to_domain(
        PasskeyRequest(
            passkey_id="passkey:credential-1",
            assertion="accepted-passkey-assertion",
        )
    )
    unknown = mapper.to_domain(
        PasskeyRequest(
            passkey_id="passkey:missing",
            assertion="wrong-passkey-assertion",
        )
    )

    assert known == (
        Identification(identifier="passkey:credential-1"),
        Credential(
            type="PASSKEY_ASSERTION",
            value="accepted-passkey-assertion",
        ),
    )
    assert unknown == (
        Identification(identifier="passkey:missing"),
        Credential(
            type="PASSKEY_ASSERTION",
            value="wrong-passkey-assertion",
        ),
    )
