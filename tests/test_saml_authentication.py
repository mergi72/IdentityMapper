import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
    IdentityTarget,
    TargetIdentity,
)
from identity_mapper.providers.saml import (
    InMemorySamlAssertionStore,
    SamlAssertionRecord,
    SamlAuthenticationError,
    SamlAuthenticator,
    SamlCredentialVerifier,
    SamlIdentityResolver,
    SamlMapper,
    SamlRequest,
    SamlTargetIdentityMapper,
    SamlTargetProjectionConfig,
)


def make_store() -> InMemorySamlAssertionStore:
    return InMemorySamlAssertionStore(
        [
            SamlAssertionRecord(
                assertion_id="saml:assertion-1",
                name_id="subject@example.org",
                assertion="accepted-saml-assertion",
                identity_id="identity-saml-1",
                issuer="example-idp",
                audience="example-sp",
                session_index="session-1",
                display_name="Example SAML Subject",
                email="subject@example.org",
                roles=("employee", "saml"),
                claims={"department": "engineering"},
                attributes={"source": "saml"},
            ),
            SamlAssertionRecord(
                assertion_id="saml:inactive",
                name_id="inactive@example.org",
                assertion="inactive-saml-assertion",
                identity_id="identity-inactive-saml",
                active=False,
            ),
        ]
    )


def test_valid_saml_assertion_returns_identity() -> None:
    identification, credential = SamlMapper().to_domain(
        SamlRequest(
            name_id="subject@example.org",
            assertion="accepted-saml-assertion",
            issuer="example-idp",
            audience="example-sp",
            session_index="session-1",
        )
    )

    identity = SamlAuthenticator(make_store()).authenticate(
        identification,
        credential,
    )

    assert identity == Identity(
        id="identity-saml-1",
        display_name="Example SAML Subject",
        email="subject@example.org",
        roles=("employee", "saml"),
        claims={"department": "engineering"},
        attributes={"source": "saml"},
    )


def test_invalid_saml_assertion_raises_authentication_failure() -> None:
    identification, credential = SamlMapper().to_domain(
        SamlRequest(
            name_id="subject@example.org",
            assertion="wrong-saml-assertion",
        )
    )

    with pytest.raises(SamlAuthenticationError):
        SamlAuthenticator(make_store()).authenticate(
            identification,
            credential,
        )


def test_unknown_saml_name_id_resolves_to_none() -> None:
    candidate = SamlIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="missing@example.org")
    )

    assert candidate is None


def test_inactive_saml_assertion_resolves_to_none() -> None:
    candidate = SamlIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="inactive@example.org")
    )

    assert candidate is None


def test_saml_resolver_returns_candidate_not_identity() -> None:
    candidate = SamlIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="subject@example.org")
    )

    assert candidate == IdentityCandidate(
        implementation_id="saml:assertion-1",
        identification=Identification(identifier="subject@example.org"),
        attributes={"source": "saml"},
    )


def test_saml_verifier_checks_candidate_and_credential() -> None:
    candidate = IdentityCandidate(
        implementation_id="saml:assertion-1",
        identification=Identification(identifier="subject@example.org"),
    )

    assert SamlCredentialVerifier(make_store()).verify_credential(
        candidate,
        Credential(type="SAML_ASSERTION", value="accepted-saml-assertion"),
    )


def test_saml_mapper_contains_no_auth_logic() -> None:
    mapper = SamlMapper()

    known = mapper.to_domain(
        SamlRequest(
            name_id="subject@example.org",
            assertion="accepted-saml-assertion",
        )
    )
    unknown = mapper.to_domain(
        SamlRequest(
            name_id="missing@example.org",
            assertion="wrong-saml-assertion",
        )
    )

    assert known == (
        Identification(identifier="subject@example.org"),
        Credential(type="SAML_ASSERTION", value="accepted-saml-assertion"),
    )
    assert unknown == (
        Identification(identifier="missing@example.org"),
        Credential(type="SAML_ASSERTION", value="wrong-saml-assertion"),
    )


def test_saml_target_mapper_projects_identity_to_saml_shape() -> None:
    identity = Identity(
        id="subject",
        email="subject@example.org",
        roles=("employee",),
        claims={"department": "engineering"},
        attributes={"source": "kerberos"},
    )
    target = IdentityTarget(provider="saml", realm="idp", purpose="sp")

    target_identity = SamlTargetIdentityMapper().map_identity(identity, target)

    assert target_identity == TargetIdentity(
        identifier="saml:subject@example.org",
        target=target,
        attributes={
            "name_id_candidate": "subject@example.org",
            "issuer_hint": "idp",
            "audience_hint": "sp",
            "attribute_hints": {"source": "kerberos"},
            "claim_hints": {"department": "engineering"},
            "role_hints": ("employee",),
        },
    )


def test_saml_target_mapper_can_use_default_issuer_and_audience() -> None:
    identity = Identity(id="subject")
    target = IdentityTarget(provider="saml")

    target_identity = SamlTargetIdentityMapper(
        SamlTargetProjectionConfig(default_issuer="idp", default_audience="sp")
    ).map_identity(identity, target)

    assert target_identity is not None
    assert target_identity.attributes["issuer_hint"] == "idp"
    assert target_identity.attributes["audience_hint"] == "sp"


def test_saml_target_mapper_does_not_issue_or_verify_assertion() -> None:
    identity = Identity(id="missing-assertion")
    target = IdentityTarget(provider="saml", realm="idp")

    target_identity = SamlTargetIdentityMapper().map_identity(identity, target)

    assert target_identity is not None
    assert target_identity.attributes["name_id_candidate"] == "missing-assertion"
    assert "assertion" not in target_identity.attributes


def test_saml_target_mapper_ignores_non_saml_target() -> None:
    assert (
        SamlTargetIdentityMapper().map_identity(
            Identity(id="subject"),
            IdentityTarget(provider="jwt"),
        )
        is None
    )
