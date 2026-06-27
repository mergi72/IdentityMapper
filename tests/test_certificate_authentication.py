import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper_certificate import (
    ClientCertificateAuthenticationError,
    ClientCertificateAuthenticator,
    ClientCertificateCredentialVerifier,
    ClientCertificateIdentityResolver,
    ClientCertificateMapper,
    ClientCertificateRecord,
    ClientCertificateRequest,
    InMemoryClientCertificateStore,
)


def make_store() -> InMemoryClientCertificateStore:
    return InMemoryClientCertificateStore(
        [
            ClientCertificateRecord(
                fingerprint="cert:fingerprint-1",
                proof="accepted-certificate-proof",
                identity_id="identity-certificate-1",
                subject="CN=example-client",
                issuer="CN=example-ca",
                serial_number="1001",
                display_name="Example Certificate Client",
                email="certificate-client@example.org",
                roles=("service", "mtls"),
                claims={"certificate": "trusted"},
                attributes={"source": "client-certificate"},
            ),
            ClientCertificateRecord(
                fingerprint="cert:inactive",
                proof="inactive-certificate-proof",
                identity_id="identity-inactive-certificate",
                active=False,
            ),
        ]
    )


def test_valid_client_certificate_returns_identity() -> None:
    identification, credential = ClientCertificateMapper().to_domain(
        ClientCertificateRequest(
            fingerprint="cert:fingerprint-1",
            proof="accepted-certificate-proof",
            subject="CN=example-client",
            issuer="CN=example-ca",
            serial_number="1001",
        )
    )

    identity = ClientCertificateAuthenticator(make_store()).authenticate(
        identification,
        credential,
    )

    assert identity == Identity(
        id="identity-certificate-1",
        display_name="Example Certificate Client",
        email="certificate-client@example.org",
        roles=("service", "mtls"),
        claims={"certificate": "trusted"},
        attributes={"source": "client-certificate"},
    )


def test_invalid_client_certificate_proof_raises_authentication_failure(
) -> None:
    identification, credential = ClientCertificateMapper().to_domain(
        ClientCertificateRequest(
            fingerprint="cert:fingerprint-1",
            proof="wrong-certificate-proof",
        )
    )

    with pytest.raises(ClientCertificateAuthenticationError):
        ClientCertificateAuthenticator(make_store()).authenticate(
            identification,
            credential,
        )


def test_unknown_client_certificate_resolves_to_none() -> None:
    candidate = ClientCertificateIdentityResolver(
        make_store()
    ).resolve_identity(Identification(identifier="cert:missing"))

    assert candidate is None


def test_inactive_client_certificate_resolves_to_none() -> None:
    candidate = ClientCertificateIdentityResolver(
        make_store()
    ).resolve_identity(Identification(identifier="cert:inactive"))

    assert candidate is None


def test_client_certificate_resolver_returns_candidate_not_identity() -> None:
    candidate = ClientCertificateIdentityResolver(
        make_store()
    ).resolve_identity(Identification(identifier="cert:fingerprint-1"))

    assert candidate == IdentityCandidate(
        implementation_id="cert:fingerprint-1",
        identification=Identification(identifier="cert:fingerprint-1"),
        attributes={"source": "client-certificate"},
    )


def test_client_certificate_verifier_checks_candidate_and_credential() -> None:
    candidate = IdentityCandidate(
        implementation_id="cert:fingerprint-1",
        identification=Identification(identifier="cert:fingerprint-1"),
    )

    assert ClientCertificateCredentialVerifier(
        make_store()
    ).verify_credential(
        candidate,
        Credential(
            type="CERTIFICATE_PROOF",
            value="accepted-certificate-proof",
        ),
    )


def test_client_certificate_mapper_contains_no_auth_logic() -> None:
    mapper = ClientCertificateMapper()

    known = mapper.to_domain(
        ClientCertificateRequest(
            fingerprint="cert:fingerprint-1",
            proof="accepted-certificate-proof",
        )
    )
    unknown = mapper.to_domain(
        ClientCertificateRequest(
            fingerprint="cert:missing",
            proof="wrong-certificate-proof",
        )
    )

    assert known == (
        Identification(identifier="cert:fingerprint-1"),
        Credential(
            type="CERTIFICATE_PROOF",
            value="accepted-certificate-proof",
        ),
    )
    assert unknown == (
        Identification(identifier="cert:missing"),
        Credential(
            type="CERTIFICATE_PROOF",
            value="wrong-certificate-proof",
        ),
    )
