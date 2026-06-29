import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
    IdentityTarget,
    TargetIdentity,
)
from identity_mapper.providers.windows import (
    InMemoryWindowsIdentityStore,
    WindowsAuthenticationError,
    WindowsAdTargetIdentityMapper,
    WindowsAdTargetProjectionConfig,
    WindowsAuthenticator,
    WindowsCredentialVerifier,
    WindowsIdentityRecord,
    WindowsIdentityRequest,
    WindowsIdentityResolver,
    WindowsMapper,
)


def make_store() -> InMemoryWindowsIdentityStore:
    return InMemoryWindowsIdentityStore(
        [
            WindowsIdentityRecord(
                sid="S-1-5-21-1000-1001",
                logon_proof="accepted-windows-logon-proof",
                identity_id="identity-windows-1",
                upn="subject@example.org",
                domain="EXAMPLE",
                display_name="Example Windows Subject",
                email="subject@example.org",
                roles=("employee", "windows"),
                claims={"domain": "EXAMPLE"},
                attributes={"source": "windows"},
            ),
            WindowsIdentityRecord(
                sid="S-1-5-21-1000-9999",
                logon_proof="inactive-windows-logon-proof",
                identity_id="identity-inactive-windows",
                active=False,
            ),
        ]
    )


def test_valid_windows_logon_proof_returns_identity() -> None:
    identification, credential = WindowsMapper().to_domain(
        WindowsIdentityRequest(
            sid="S-1-5-21-1000-1001",
            logon_proof="accepted-windows-logon-proof",
            upn="subject@example.org",
            domain="EXAMPLE",
        )
    )

    identity = WindowsAuthenticator(make_store()).authenticate(
        identification,
        credential,
    )

    assert identity == Identity(
        id="identity-windows-1",
        display_name="Example Windows Subject",
        email="subject@example.org",
        roles=("employee", "windows"),
        claims={"domain": "EXAMPLE"},
        attributes={"source": "windows"},
    )


def test_invalid_windows_logon_proof_raises_authentication_failure() -> None:
    identification, credential = WindowsMapper().to_domain(
        WindowsIdentityRequest(
            sid="S-1-5-21-1000-1001",
            logon_proof="wrong-windows-logon-proof",
        )
    )

    with pytest.raises(WindowsAuthenticationError):
        WindowsAuthenticator(make_store()).authenticate(
            identification,
            credential,
        )


def test_unknown_windows_sid_resolves_to_none() -> None:
    candidate = WindowsIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="S-1-5-21-1000-4040")
    )

    assert candidate is None


def test_inactive_windows_sid_resolves_to_none() -> None:
    candidate = WindowsIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="S-1-5-21-1000-9999")
    )

    assert candidate is None


def test_windows_resolver_returns_candidate_not_identity() -> None:
    candidate = WindowsIdentityResolver(make_store()).resolve_identity(
        Identification(identifier="S-1-5-21-1000-1001")
    )

    assert candidate == IdentityCandidate(
        implementation_id="S-1-5-21-1000-1001",
        identification=Identification(identifier="S-1-5-21-1000-1001"),
        attributes={"source": "windows"},
    )


def test_windows_verifier_checks_candidate_and_credential() -> None:
    candidate = IdentityCandidate(
        implementation_id="S-1-5-21-1000-1001",
        identification=Identification(identifier="S-1-5-21-1000-1001"),
    )

    assert WindowsCredentialVerifier(make_store()).verify_credential(
        candidate,
        Credential(
            type="WINDOWS_LOGON_PROOF",
            value="accepted-windows-logon-proof",
        ),
    )


def test_windows_mapper_contains_no_auth_logic() -> None:
    mapper = WindowsMapper()

    known = mapper.to_domain(
        WindowsIdentityRequest(
            sid="S-1-5-21-1000-1001",
            logon_proof="accepted-windows-logon-proof",
        )
    )
    unknown = mapper.to_domain(
        WindowsIdentityRequest(
            sid="S-1-5-21-1000-4040",
            logon_proof="wrong-windows-logon-proof",
        )
    )

    assert known == (
        Identification(identifier="S-1-5-21-1000-1001"),
        Credential(
            type="WINDOWS_LOGON_PROOF",
            value="accepted-windows-logon-proof",
        ),
    )
    assert unknown == (
        Identification(identifier="S-1-5-21-1000-4040"),
        Credential(
            type="WINDOWS_LOGON_PROOF",
            value="wrong-windows-logon-proof",
        ),
    )


def test_windows_ad_target_mapper_projects_identity_to_ad_shape() -> None:
    identity = Identity(
        id="subject",
        display_name="Example Subject",
        email="subject@corp.local",
        roles=("employees", "readers"),
        attributes={"source": "kerberos"},
    )
    target = IdentityTarget(
        provider="ad",
        realm="corp.local",
        purpose="bind_identity",
    )

    target_identity = WindowsAdTargetIdentityMapper().map_identity(identity, target)

    assert target_identity == TargetIdentity(
        identifier="ad:subject@corp.local",
        target=target,
        attributes={
            "upn_candidate": "subject@corp.local",
            "sam_account_name_candidate": "subject",
            "mail_hint": "subject@corp.local",
            "group_hints": ("employees", "readers"),
        },
    )


def test_windows_ad_target_mapper_uses_realm_when_email_is_missing() -> None:
    identity = Identity(id="subject", roles=("employees",))
    target = IdentityTarget(provider="ad", realm="corp.local")

    target_identity = WindowsAdTargetIdentityMapper().map_identity(identity, target)

    assert target_identity == TargetIdentity(
        identifier="ad:subject@corp.local",
        target=target,
        attributes={
            "upn_candidate": "subject@corp.local",
            "sam_account_name_candidate": "subject",
            "group_hints": ("employees",),
        },
    )


def test_windows_ad_target_mapper_can_use_default_realm() -> None:
    identity = Identity(id="subject")
    target = IdentityTarget(provider="ad")

    target_identity = WindowsAdTargetIdentityMapper(
        WindowsAdTargetProjectionConfig(default_realm="corp.local")
    ).map_identity(identity, target)

    assert target_identity == TargetIdentity(
        identifier="ad:subject@corp.local",
        target=target,
        attributes={
            "upn_candidate": "subject@corp.local",
            "sam_account_name_candidate": "subject",
            "group_hints": (),
        },
    )


def test_windows_ad_target_mapper_does_not_confirm_account_existence() -> None:
    identity = Identity(id="missing-user")
    target = IdentityTarget(provider="ad", realm="corp.local")

    target_identity = WindowsAdTargetIdentityMapper().map_identity(identity, target)

    assert target_identity is not None
    assert target_identity.attributes["upn_candidate"] == "missing-user@corp.local"


def test_windows_ad_target_mapper_ignores_non_ad_target() -> None:
    identity = Identity(id="subject")
    target = IdentityTarget(provider="ldap")

    assert WindowsAdTargetIdentityMapper().map_identity(identity, target) is None
