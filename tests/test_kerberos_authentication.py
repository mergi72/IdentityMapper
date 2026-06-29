import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
    IdentityTarget,
    TargetIdentity,
)
from identity_mapper.providers.kerberos import (
    InMemoryKerberosPrincipalStore,
    KerberosAuthenticationError,
    KerberosAuthenticator,
    KerberosCredentialVerifier,
    KerberosIdentityResolver,
    KerberosMapper,
    KerberosPrincipalRecord,
    KerberosRequest,
    KerberosTargetIdentityMapper,
    KerberosTargetProjectionConfig,
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


def test_kerberos_target_mapper_projects_identity_to_principal_shape() -> None:
    identity = Identity(id="subject", roles=("service",))
    target = IdentityTarget(
        provider="kerberos",
        realm="EXAMPLE.ORG",
        purpose="HTTP/app.example.org",
    )

    target_identity = KerberosTargetIdentityMapper().map_identity(identity, target)

    assert target_identity == TargetIdentity(
        identifier="kerberos:subject@EXAMPLE.ORG",
        target=target,
        attributes={
            "principal_candidate": "subject@EXAMPLE.ORG",
            "realm_hint": "EXAMPLE.ORG",
            "service_hint": "HTTP/app.example.org",
            "role_hints": ("service",),
        },
    )


def test_kerberos_target_mapper_can_use_default_realm() -> None:
    identity = Identity(id="subject")
    target = IdentityTarget(provider="kerberos")

    target_identity = KerberosTargetIdentityMapper(
        KerberosTargetProjectionConfig(default_realm="EXAMPLE.ORG")
    ).map_identity(identity, target)

    assert target_identity is not None
    assert target_identity.attributes["principal_candidate"] == "subject@EXAMPLE.ORG"


def test_kerberos_target_mapper_does_not_confirm_principal_existence() -> None:
    identity = Identity(id="missing-principal")
    target = IdentityTarget(provider="kerberos", realm="EXAMPLE.ORG")

    target_identity = KerberosTargetIdentityMapper().map_identity(identity, target)

    assert target_identity is not None
    assert (
        target_identity.attributes["principal_candidate"]
        == "missing-principal@EXAMPLE.ORG"
    )


def test_kerberos_target_mapper_ignores_non_kerberos_target() -> None:
    assert (
        KerberosTargetIdentityMapper().map_identity(
            Identity(id="subject"),
            IdentityTarget(provider="ldap"),
        )
        is None
    )
