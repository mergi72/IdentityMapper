import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
    IdentityTarget,
    TargetIdentity,
)
from identity_mapper.providers.ldap import (
    InMemoryLdapDirectory,
    LdapAuthenticationError,
    LdapAuthenticator,
    LdapBindMapper,
    LdapBindRequest,
    LdapCredentialVerifier,
    LdapEntry,
    LdapIdentityResolver,
    LdapTargetIdentityMapper,
    LdapTargetProjectionConfig,
)


def make_directory() -> InMemoryLdapDirectory:
    return InMemoryLdapDirectory(
        [
            LdapEntry(
                dn="uid=subject,ou=people,dc=example,dc=org",
                uid="subject",
                user_password="accepted",
                identity_id="identity-ldap-1",
                cn="Example Subject",
                mail="subject@example.org",
                groups=("readers",),
                claims={"directory": "ldap"},
                attributes={"source": "ldap"},
            ),
            LdapEntry(
                dn="uid=inactive,ou=people,dc=example,dc=org",
                uid="inactive",
                user_password="inactive",
                identity_id="identity-inactive-ldap",
                active=False,
            ),
        ]
    )


def test_valid_ldap_bind_returns_identity() -> None:
    identification, credential = LdapBindMapper().to_domain(
        LdapBindRequest(
            uid="subject",
            password="accepted",
        )
    )

    identity = LdapAuthenticator(make_directory()).authenticate(
        identification,
        credential,
    )

    assert identity == Identity(
        id="identity-ldap-1",
        display_name="Example Subject",
        email="subject@example.org",
        roles=("readers",),
        claims={"directory": "ldap"},
        attributes={"source": "ldap"},
    )


def test_invalid_ldap_password_raises_authentication_failure() -> None:
    identification, credential = LdapBindMapper().to_domain(
        LdapBindRequest(
            uid="subject",
            password="wrong",
        )
    )

    with pytest.raises(LdapAuthenticationError):
        LdapAuthenticator(make_directory()).authenticate(
            identification,
            credential,
        )


def test_unknown_ldap_user_resolves_to_none() -> None:
    candidate = LdapIdentityResolver(make_directory()).resolve_identity(
        Identification(identifier="missing")
    )

    assert candidate is None


def test_inactive_ldap_user_resolves_to_none() -> None:
    candidate = LdapIdentityResolver(make_directory()).resolve_identity(
        Identification(identifier="inactive")
    )

    assert candidate is None


def test_ldap_resolver_returns_candidate_not_identity() -> None:
    candidate = LdapIdentityResolver(make_directory()).resolve_identity(
        Identification(identifier="subject")
    )

    assert candidate == IdentityCandidate(
        implementation_id="uid=subject,ou=people,dc=example,dc=org",
        identification=Identification(identifier="subject"),
        attributes={"source": "ldap"},
    )


def test_ldap_verifier_checks_candidate_and_credential() -> None:
    candidate = IdentityCandidate(
        implementation_id="uid=subject,ou=people,dc=example,dc=org",
        identification=Identification(identifier="subject"),
    )

    assert LdapCredentialVerifier(make_directory()).verify_credential(
        candidate,
        Credential(type="PASSWORD", value="accepted"),
    )


def test_ldap_verifier_rejects_inactive_candidate() -> None:
    candidate = IdentityCandidate(
        implementation_id="uid=inactive,ou=people,dc=example,dc=org",
        identification=Identification(identifier="inactive"),
    )

    assert not LdapCredentialVerifier(make_directory()).verify_credential(
        candidate,
        Credential(type="PASSWORD", value="inactive"),
    )


def test_ldap_mapper_contains_no_auth_logic() -> None:
    mapper = LdapBindMapper()

    known = mapper.to_domain(
        LdapBindRequest(uid="subject", password="accepted")
    )
    unknown = mapper.to_domain(
        LdapBindRequest(uid="missing", password="wrong")
    )

    assert known == (
        Identification(identifier="subject"),
        Credential(type="PASSWORD", value="accepted"),
    )
    assert unknown == (
        Identification(identifier="missing"),
        Credential(type="PASSWORD", value="wrong"),
    )


def test_ldap_target_mapper_projects_identity_to_ldap_shape() -> None:
    identity = Identity(
        id="subject@example.org",
        display_name="Example Subject",
        email="subject@example.org",
        roles=("readers",),
    )
    target = IdentityTarget(provider="ldap", realm="ou=people,dc=example,dc=org")

    target_identity = LdapTargetIdentityMapper().map_identity(identity, target)

    assert target_identity == TargetIdentity(
        identifier="ldap:uid=subject,ou=people,dc=example,dc=org",
        target=target,
        attributes={
            "uid_candidate": "subject",
            "dn_candidate": "uid=subject,ou=people,dc=example,dc=org",
            "cn_hint": "Example Subject",
            "mail_hint": "subject@example.org",
            "group_hints": ("readers",),
        },
    )


def test_ldap_target_mapper_can_use_default_base_dn() -> None:
    identity = Identity(id="subject")
    target = IdentityTarget(provider="ldap")

    target_identity = LdapTargetIdentityMapper(
        LdapTargetProjectionConfig(default_base_dn="ou=people,dc=example,dc=org")
    ).map_identity(identity, target)

    assert target_identity is not None
    assert (
        target_identity.attributes["dn_candidate"]
        == "uid=subject,ou=people,dc=example,dc=org"
    )


def test_ldap_target_mapper_does_not_confirm_entry_existence() -> None:
    identity = Identity(id="missing-user")
    target = IdentityTarget(provider="ldap", realm="ou=people,dc=example,dc=org")

    target_identity = LdapTargetIdentityMapper().map_identity(identity, target)

    assert target_identity is not None
    assert target_identity.attributes["uid_candidate"] == "missing-user"


def test_ldap_target_mapper_ignores_non_ldap_target() -> None:
    assert (
        LdapTargetIdentityMapper().map_identity(
            Identity(id="subject"),
            IdentityTarget(provider="ad"),
        )
        is None
    )
