from identity_mapper.capabilities import Authenticate
from identity_mapper.domain import Credential, Identification, Identity


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
                identifier=identification.identifier,
            )

        raise ValueError("invalid credential")


def test_authenticate_returns_verified_identity() -> None:
    identity = ExampleAuthenticator().authenticate(
        Identification(identifier="subject"),
        Credential(type="opaque", value="accepted"),
    )

    assert identity == Identity(
        id="identity-1",
        identifier="subject",
    )
