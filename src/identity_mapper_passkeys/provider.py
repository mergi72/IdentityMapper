from identity_mapper_passkeys.domain import PasskeyRecord


class InMemoryPasskeyStore:
    """In-memory provider for passkey records."""

    def __init__(self, passkeys: list[PasskeyRecord] | None = None) -> None:
        self._by_passkey_id: dict[str, PasskeyRecord] = {}

        for passkey in passkeys or []:
            self.add(passkey)

    def add(self, passkey: PasskeyRecord) -> None:
        self._by_passkey_id[passkey.passkey_id] = passkey

    def get_by_passkey_id(self, passkey_id: str) -> PasskeyRecord | None:
        return self._by_passkey_id.get(passkey_id)
