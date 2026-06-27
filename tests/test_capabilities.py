from identity_mapper.capabilities import (
    Authenticate,
    ResolveIdentity,
    VerifyCredential,
)
from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)


class ExampleAuthenticator(Authenticate):
    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        if (
            identification.identifier == "subject"
            and credential.value == "accepted"
        ):
            return Identity(
                id="identity-1",
            )

        raise ValueError("invalid credential")


class ExampleIdentityResolver(ResolveIdentity):
    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        if identification.identifier != "subject":
            return None

        return IdentityCandidate(
            id="identity-1",
            identification=identification,
        )


class ExampleCredentialVerifier(VerifyCredential):
    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        return candidate.id == "identity-1" and credential.value == "accepted"


def test_authenticate_returns_verified_identity() -> None:
    identity = ExampleAuthenticator().authenticate(
        Identification(identifier="subject"),
        Credential(type="opaque", value="accepted"),
    )

    assert identity == Identity(
        id="identity-1",
    )


def test_resolve_identity_returns_unverified_candidate() -> None:
    identification = Identification(identifier="subject")

    candidate = ExampleIdentityResolver().resolve_identity(identification)

    assert candidate == IdentityCandidate(
        id="identity-1",
        identification=identification,
    )


def test_verify_credential_checks_candidate() -> None:
    candidate = IdentityCandidate(
        id="identity-1",
        identification=Identification(identifier="subject"),
    )

    assert ExampleCredentialVerifier().verify_credential(
        candidate,
        Credential(type="opaque", value="accepted"),
    )
