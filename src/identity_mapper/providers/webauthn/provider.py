from identity_mapper.providers.webauthn.domain import WebAuthnCredentialRecord


class InMemoryWebAuthnCredentialStore:
    """In-memory provider for WebAuthn credential records."""

    def __init__(
        self,
        credentials: list[WebAuthnCredentialRecord] | None = None,
    ) -> None:
        self._by_credential_id: dict[str, WebAuthnCredentialRecord] = {}

        for credential in credentials or []:
            self.add(credential)

    def add(self, credential: WebAuthnCredentialRecord) -> None:
        self._by_credential_id[credential.credential_id] = credential

    def get_by_credential_id(
        self,
        credential_id: str,
    ) -> WebAuthnCredentialRecord | None:
        return self._by_credential_id.get(credential_id)
