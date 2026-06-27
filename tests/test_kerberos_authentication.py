import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper_kerberos import (
    InMemoryKerberosPrincipalStore,
    KerberosAuthenticationError,
    KerberosAuthenticator,
    KerberosCredentialVerifier,
    KerberosIdentityResolver,
    KerberosMapper,
    KerberosPrincipalRecord,
    KerberosRequest,
)


def make_store() -> InMemoryKerberosPrincipalStore:
    return InMemoryKerberosPrincipalStore(
        [
            KerberosPrincipalRecord(
                principal="service/example@EXAMPLE.ORG",
                ticket="accepted-kerberos-ticket",
                identity_id="identity-kerberos-1",
                realm="EXAMPLE.ORG",
                service="service/example",
                display_name="Example Kerberos Principal",
                email="kerberos-principal@example.org",
                roles=("service", "kerberos"),
                claims={"realm": "EXAMPLE.ORG"},
                attributes={"source": "kerberos"},
            ),
            KerberosPrincipalRecord(
                principal="inactive@EXAMPLE.ORG",
                ticket="inactive-kerberos-ticket",
                identity_id="identity-inactive-kerberos",
                active=False,
            ),
        ]
    )


def test_valid_kerberos_ticket_returns_identity() -> None:
    identification, credential = KerberosMapper().to_domain(
        KerberosRequest(
            principal="service/example@EXAMPLE.ORG",
            ticket="accepted-kerberos-ticket",
            realm="EXAMPLE.ORG",
            service="service/example",
        )
    )

    identity = KerberosAuthenticator(make_store()).authenticate(
        identification,
        credential,
    )

    assert identity == Identity(
        id="identity-kerberos-1",
        display_name="Example Kerberos Principal",
        email="kerberos-principal@example.org",
        roles=("service", "kerberos"),
        claims={"realm": "EXAMPLE.ORG"},
        attributes={"source": "kerberos"},
    )


def test_invalid_kerberos_ticket_raises_authentication_failure() -> None:
    identification, credential = KerberosMapper().to_domain(
        KerberosRequest(
            principal="service/example@EXAMPLE.ORG",
            ticket="wrong-kerberos-ticket",
        )
    )

    with pytest.raises(KerberosAuthenticationError):
        KerberosAuthenticator(make_store()).authenticate(
            identification,
            credential,
        )


def test_unknown_kerberos_principal_resolves_to_none() -> None:
    candidate = KerberosIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="missing@EXAMPLE.ORG")
    )

    assert candidate is None


def test_inactive_kerberos_principal_resolves_to_none() -> None:
    candidate = KerberosIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="inactive@EXAMPLE.ORG")
    )

    assert candidate is None


def test_kerberos_resolver_returns_candidate_not_identity() -> None:
    candidate = KerberosIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="service/example@EXAMPLE.ORG")
    )

    assert candidate == IdentityCandidate(
        implementation_id="service/example@EXAMPLE.ORG",
        identification=Identification(
            identifier="service/example@EXAMPLE.ORG"
        ),
        attributes={"source": "kerberos"},
    )


def test_kerberos_verifier_checks_candidate_and_credential() -> None:
    candidate = IdentityCandidate(
        implementation_id="service/example@EXAMPLE.ORG",
        identification=Identification(
            identifier="service/example@EXAMPLE.ORG"
        ),
    )

    assert KerberosCredentialVerifier(make_store()).verify_credential(
        candidate,
        Credential(
            type="KERBEROS_TICKET",
            value="accepted-kerberos-ticket",
        ),
    )


def test_kerberos_mapper_contains_no_auth_logic() -> None:
    mapper = KerberosMapper()

    known = mapper.to_domain(
        KerberosRequest(
            principal="service/example@EXAMPLE.ORG",
            ticket="accepted-kerberos-ticket",
        )
    )
    unknown = mapper.to_domain(
        KerberosRequest(
            principal="missing@EXAMPLE.ORG",
            ticket="wrong-kerberos-ticket",
        )
    )

    assert known == (
        Identification(identifier="service/example@EXAMPLE.ORG"),
        Credential(
            type="KERBEROS_TICKET",
            value="accepted-kerberos-ticket",
        ),
    )
    assert unknown == (
        Identification(identifier="missing@EXAMPLE.ORG"),
        Credential(
            type="KERBEROS_TICKET",
            value="wrong-kerberos-ticket",
        ),
    )
