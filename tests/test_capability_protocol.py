from identity_mapper import (
    Credential,
    Identification,
)
from identity_mapper.capability_protocol import (
    AuthenticationRejected,
    AuthenticateRequest,
    AuthenticateResponse,
    ResolveIdentityRequest,
    ResolveIdentityResponse,
    VerifyCredentialRequest,
    VerifyCredentialResponse,
)
from identity_mapper.domain import Identity, IdentityCandidate


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
