from identity_mapper.domain import Credential, Identification
from identity_mapper.implementations.basic import (
    BasicAuthenticationMapper,
    BasicAuthenticationRequest,
)


def test_basic_authentication_mapper_maps_to_existing_domain_inputs() -> None:
    request = BasicAuthenticationRequest(
        identifier="subject",
        secret="accepted",
        realm="example",
        metadata={"source": "test"},
    )

    identification, credential = BasicAuthenticationMapper().to_domain(request)

    assert identification == Identification(
        identifier="subject",
        realm="example",
    )
    assert credential == Credential(
        type="PASSWORD",
        value="accepted",
        metadata={"source": "test"},
    )


def test_basic_authentication_request_repr_does_not_expose_secret() -> None:
    request = BasicAuthenticationRequest(
        identifier="subject",
        secret="sensitive",
    )

    assert "sensitive" not in repr(request)
