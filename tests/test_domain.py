from identity_mapper.domain import Credential


def test_credential_repr_does_not_expose_value() -> None:
    credential = Credential(type="opaque", value="sensitive")

    assert "sensitive" not in repr(credential)
