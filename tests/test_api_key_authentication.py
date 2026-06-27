import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper_api_key import (
    ApiKeyAuthenticationError,
    ApiKeyAuthenticator,
    ApiKeyCredentialVerifier,
    ApiKeyIdentityResolver,
    ApiKeyMapper,
    ApiKeyRecord,
    ApiKeyRequest,
    InMemoryApiKeyStore,
)


def make_store() -> InMemoryApiKeyStore:
    return InMemoryApiKeyStore(
        [
            ApiKeyRecord(
                key_id="key-1",
                api_key="accepted-key",
                identity_id="identity-api-key-1",
                client_id="client-1",
                display_name="Example Client",
                email="client@example.org",
                roles=("service",),
                claims={"scope": "payments"},
                attributes={"source": "api-key"},
            ),
            ApiKeyRecord(
                key_id="inactive-key",
                api_key="inactive-key-secret",
                identity_id="identity-inactive-key",
                active=False,
            ),
        ]
    )


def test_valid_api_key_returns_identity() -> None:
    identification, credential = ApiKeyMapper().to_domain(
        ApiKeyRequest(
            key_id="key-1",
            api_key="accepted-key",
            client_id="client-1",
        )
    )

    identity = ApiKeyAuthenticator(make_store()).authenticate(
        identification,
        credential,
    )

    assert identity == Identity(
        id="identity-api-key-1",
        display_name="Example Client",
        email="client@example.org",
        roles=("service",),
        claims={"scope": "payments"},
        attributes={"source": "api-key"},
    )


def test_invalid_api_key_raises_authentication_failure() -> None:
    identification, credential = ApiKeyMapper().to_domain(
        ApiKeyRequest(
            key_id="key-1",
            api_key="wrong-key",
        )
    )

    with pytest.raises(ApiKeyAuthenticationError):
        ApiKeyAuthenticator(make_store()).authenticate(
            identification,
            credential,
        )


def test_unknown_api_key_resolves_to_none() -> None:
    candidate = ApiKeyIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="missing-key")
    )

    assert candidate is None


def test_inactive_api_key_resolves_to_none() -> None:
    candidate = ApiKeyIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="inactive-key")
    )

    assert candidate is None


def test_api_key_resolver_returns_candidate_not_identity() -> None:
    candidate = ApiKeyIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="key-1")
    )

    assert candidate == IdentityCandidate(
        implementation_id="key-1",
        identification=Identification(identifier="key-1"),
        attributes={"source": "api-key"},
    )


def test_api_key_verifier_checks_candidate_and_credential() -> None:
    candidate = IdentityCandidate(
        implementation_id="key-1",
        identification=Identification(identifier="key-1"),
    )

    assert ApiKeyCredentialVerifier(make_store()).verify_credential(
        candidate,
        Credential(type="API_KEY", value="accepted-key"),
    )


def test_api_key_mapper_contains_no_auth_logic() -> None:
    mapper = ApiKeyMapper()

    known = mapper.to_domain(
        ApiKeyRequest(key_id="key-1", api_key="accepted-key")
    )
    unknown = mapper.to_domain(
        ApiKeyRequest(key_id="missing-key", api_key="wrong-key")
    )

    assert known == (
        Identification(identifier="key-1"),
        Credential(type="API_KEY", value="accepted-key"),
    )
    assert unknown == (
        Identification(identifier="missing-key"),
        Credential(type="API_KEY", value="wrong-key"),
    )
