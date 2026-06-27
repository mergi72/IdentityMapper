from identity_mapper_windows.domain import WindowsIdentityRecord


class InMemoryWindowsIdentityStore:
    """In-memory provider for Windows identity records."""

    def __init__(
        self,
        identities: list[WindowsIdentityRecord] | None = None,
    ) -> None:
        self._by_sid: dict[str, WindowsIdentityRecord] = {}

        for identity in identities or []:
            self.add(identity)

    def add(self, identity: WindowsIdentityRecord) -> None:
        self._by_sid[identity.sid] = identity

    def get_by_sid(self, sid: str) -> WindowsIdentityRecord | None:
        return self._by_sid.get(sid)
