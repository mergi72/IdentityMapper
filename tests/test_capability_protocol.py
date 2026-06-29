from identity_mapper import (
    Credential,
    Identification,
)
from identity_mapper.capability_protocol import (
    AuthenticationRejected,
    AuthenticateRequest,
    AuthenticateResponse,
    MapIdentityRequest,
    MapIdentityResponse,
    ResolveIdentityRequest,
    ResolveIdentityResponse,
    VerifyCredentialRequest,
    VerifyCredentialResponse,
)
from identity_mapper.domain import Identity, IdentityCandidate, IdentityTarget, TargetIdentity


def test_authenticate_request_carries_domain_inputs() -> None:
    identification = Identification(identifier="subject")
    credential = Credential(type="PASSWORD", value="accepted")

    request = AuthenticateRequest(
        provider="basic",
        identification=identification,
        credential=credential,
    )

    assert request.provider == "basic"
    assert request.identification is identification
    assert request.credential is credential


def test_authenticate_request_can_defer_provider_selection() -> None:
    identification = Identification(identifier="subject")
    credential = Credential(type="PASSWORD", value="accepted")

    request = AuthenticateRequest(
        identification=identification,
        credential=credential,
    )

    assert request.provider is None
    assert request.identification is identification
    assert request.credential is credential


def test_authenticate_response_carries_authenticated_identity() -> None:
    identity = Identity(id="identity-1", display_name="Example Subject")

    response = AuthenticateResponse(authenticated=True, identity=identity)

    assert response.authenticated
    assert response.identity is identity
    assert response.error is None


def test_authentication_rejected_is_protocol_signal() -> None:
    assert issubclass(AuthenticationRejected, Exception)


def test_resolve_identity_request_and_response() -> None:
    identification = Identification(identifier="subject")
    candidate = IdentityCandidate(
        implementation_id="basic:subject",
        identification=identification,
    )

    request = ResolveIdentityRequest(
        provider="basic",
        identification=identification,
    )
    response = ResolveIdentityResponse(candidate=candidate)

    assert request.provider == "basic"
    assert response.candidate is candidate


def test_resolve_identity_request_can_defer_provider_selection() -> None:
    identification = Identification(identifier="subject")

    request = ResolveIdentityRequest(identification=identification)

    assert request.provider is None
    assert request.identification is identification


def test_verify_credential_request_and_response() -> None:
    identification = Identification(identifier="subject")
    candidate = IdentityCandidate(
        implementation_id="basic:subject",
        identification=identification,
    )
    credential = Credential(type="PASSWORD", value="accepted")

    request = VerifyCredentialRequest(
        provider="basic",
        candidate=candidate,
        credential=credential,
    )
    response = VerifyCredentialResponse(verified=True)

    assert request.provider == "basic"
    assert request.candidate is candidate
    assert request.credential is credential
    assert response.verified


def test_verify_credential_request_can_defer_provider_selection() -> None:
    identification = Identification(identifier="subject")
    candidate = IdentityCandidate(
        implementation_id="basic:subject",
        identification=identification,
    )
    credential = Credential(type="PASSWORD", value="accepted")

    request = VerifyCredentialRequest(
        candidate=candidate,
        credential=credential,
    )

    assert request.provider is None
    assert request.candidate is candidate
    assert request.credential is credential


def test_map_identity_request_and_response() -> None:
    identification = Identification(identifier="subject")
    credential = Credential(type="KERBEROS_TICKET", value="ticket")
    target = IdentityTarget(
        provider="active_directory",
        realm="corp.example",
        purpose="bind_identity",
    )
    identity = Identity(id="identity-1")
    target_identity = TargetIdentity(
        identifier="CORP\\subject",
        target=target,
    )

    request = MapIdentityRequest(
        source_provider="kerberos",
        source_identification=identification,
        source_credential=credential,
        target=target,
    )
    response = MapIdentityResponse(
        mapped=True,
        identity=identity,
        target_identity=target_identity,
    )

    assert request.source_provider == "kerberos"
    assert request.source_identification is identification
    assert request.source_credential is credential
    assert request.target is target
    assert response.mapped
    assert response.identity is identity
    assert response.target_identity is target_identity
