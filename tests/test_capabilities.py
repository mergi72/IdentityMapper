from identity_mapper.capabilities import (
    Authenticate,
    MapIdentity,
    ResolveIdentity,
    VerifyCredential,
)
from identity_mapper.capability_protocol import AuthenticationRejected
from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
    IdentityTarget,
    TargetIdentity,
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

        raise AuthenticationRejected("invalid credential")


class ExampleIdentityResolver(ResolveIdentity):
    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        if identification.identifier != "subject":
            return None

        return IdentityCandidate(
            implementation_id="candidate-1",
            identification=identification,
        )


class ExampleCredentialVerifier(VerifyCredential):
    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        return (
            candidate.implementation_id == "candidate-1"
            and credential.value == "accepted"
        )


class ExampleIdentityMapper(MapIdentity):
    def map_identity(
        self,
        identity: Identity,
        target: IdentityTarget,
    ) -> TargetIdentity | None:
        if target.provider != "target":
            return None

        return TargetIdentity(
            identifier=f"target:{identity.id}",
            target=target,
        )


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
        implementation_id="candidate-1",
        identification=identification,
    )


def test_verify_credential_checks_candidate() -> None:
    candidate = IdentityCandidate(
        implementation_id="candidate-1",
        identification=Identification(identifier="subject"),
    )

    assert ExampleCredentialVerifier().verify_credential(
        candidate,
        Credential(type="opaque", value="accepted"),
    )


def test_map_identity_returns_target_identity_projection() -> None:
    identity = Identity(id="identity-1")
    target = IdentityTarget(provider="target")

    target_identity = ExampleIdentityMapper().map_identity(identity, target)

    assert target_identity == TargetIdentity(
        identifier="target:identity-1",
        target=target,
    )
