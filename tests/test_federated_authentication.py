import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper_federated import (
    FederatedAuthenticationError,
    FederatedAuthenticator,
    FederatedCredentialVerifier,
    FederatedIdentityRecord,
    FederatedIdentityResolver,
    FederatedMapper,
    FederatedRequest,
    InMemoryFederatedIdentityStore,
)


def make_store() -> InMemoryFederatedIdentityStore:
    return InMemoryFederatedIdentityStore(
        [
            FederatedIdentityRecord(
                trust_mapping_id="federation:subject",
                issuer="example-idp",
                external_subject="external-subject",
                assertion="accepted-federation-assertion",
                identity_id="identity-federated-1",
                audience="example-app",
                display_name="Example Federated Subject",
                email="subject@example.org",
                roles=("employee", "federated"),
                claims={"issuer": "example-idp"},
                attributes={"source": "federated"},
            ),
            FederatedIdentityRecord(
                trust_mapping_id="federation:inactive",
                issuer="example-idp",
                external_subject="inactive-subject",
                assertion="inactive-federation-assertion",
                identity_id="identity-inactive-federated",
                active=False,
            ),
        ]
    )


def test_valid_federated_assertion_returns_identity() -> None:
    identification, credential = FederatedMapper().to_domain(
        FederatedRequest(
            issuer="example-idp",
            external_subject="external-subject",
            assertion="accepted-federation-assertion",
            audience="example-app",
        )
    )

    identity = FederatedAuthenticator(make_store()).authenticate(
        identification,
        credential,
    )

    assert identity == Identity(
        id="identity-federated-1",
        display_name="Example Federated Subject",
        email="subject@example.org",
        roles=("employee", "federated"),
        claims={"issuer": "example-idp"},
        attributes={"source": "federated"},
    )


def test_invalid_federated_assertion_raises_authentication_failure() -> None:
    identification, credential = FederatedMapper().to_domain(
        FederatedRequest(
            issuer="example-idp",
            external_subject="external-subject",
            assertion="wrong-federation-assertion",
        )
    )

    with pytest.raises(FederatedAuthenticationError):
        FederatedAuthenticator(make_store()).authenticate(
            identification,
            credential,
        )


def test_unknown_federated_subject_resolves_to_none() -> None:
    candidate = FederatedIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="missing-subject", realm="example-idp")
    )

    assert candidate is None


def test_unknown_federated_issuer_resolves_to_none() -> None:
    candidate = FederatedIdentityResolver(make_store()).resolve_identity(
        Identification(
            identifier="external-subject",
            realm="unknown-idp",
        )
    )

    assert candidate is None


def test_inactive_federated_mapping_resolves_to_none() -> None:
    candidate = FederatedIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="inactive-subject", realm="example-idp")
    )

    assert candidate is None


def test_federated_resolver_returns_candidate_not_identity() -> None:
    candidate = FederatedIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="external-subject", realm="example-idp")
    )

    assert candidate == IdentityCandidate(
        implementation_id="federation:subject",
        identification=Identification(
            identifier="external-subject",
            realm="example-idp",
        ),
        attributes={"source": "federated"},
    )


def test_federated_verifier_checks_candidate_and_credential() -> None:
    candidate = IdentityCandidate(
        implementation_id="federation:subject",
        identification=Identification(
            identifier="external-subject",
            realm="example-idp",
        ),
    )

    assert FederatedCredentialVerifier(make_store()).verify_credential(
        candidate,
        Credential(
            type="FEDERATION_ASSERTION",
            value="accepted-federation-assertion",
        ),
    )


def test_federated_mapper_contains_no_auth_logic() -> None:
    mapper = FederatedMapper()

    known = mapper.to_domain(
        FederatedRequest(
            issuer="example-idp",
            external_subject="external-subject",
            assertion="accepted-federation-assertion",
        )
    )
    unknown = mapper.to_domain(
        FederatedRequest(
            issuer="unknown-idp",
            external_subject="missing-subject",
            assertion="wrong-federation-assertion",
        )
    )

    assert known == (
        Identification(
            identifier="external-subject",
            realm="example-idp",
            attributes={"issuer": "example-idp"},
        ),
        Credential(
            type="FEDERATION_ASSERTION",
            value="accepted-federation-assertion",
        ),
    )
    assert unknown == (
        Identification(
            identifier="missing-subject",
            realm="unknown-idp",
            attributes={"issuer": "unknown-idp"},
        ),
        Credential(
            type="FEDERATION_ASSERTION",
            value="wrong-federation-assertion",
        ),
    )
