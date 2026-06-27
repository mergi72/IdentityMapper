import pytest

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper_windows import (
    InMemoryWindowsIdentityStore,
    WindowsAuthenticationError,
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
