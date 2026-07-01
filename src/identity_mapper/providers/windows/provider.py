from identity_mapper.providers.windows.domain import (
    WindowsAdTargetAccountRecord,
    WindowsIdentityRecord,
)


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


class InMemoryWindowsAdTargetDirectory:
    """In-memory read-only target directory for Windows / AD account lookup."""

    def __init__(
        self,
        accounts: list[WindowsAdTargetAccountRecord] | None = None,
    ) -> None:
        self._by_upn: dict[str, WindowsAdTargetAccountRecord] = {}
        self._by_sam_account_name: dict[str, WindowsAdTargetAccountRecord] = {}

        for account in accounts or []:
            self.add(account)

    def add(self, account: WindowsAdTargetAccountRecord) -> None:
        self._by_upn[account.upn.lower()] = account
        self._by_sam_account_name[account.sam_account_name.lower()] = account

    def get_by_upn(self, upn: str) -> WindowsAdTargetAccountRecord | None:
        return self._by_upn.get(upn.lower())

    def get_by_sam_account_name(
        self,
        sam_account_name: str,
    ) -> WindowsAdTargetAccountRecord | None:
        return self._by_sam_account_name.get(sam_account_name.lower())
