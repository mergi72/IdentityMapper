from __future__ import annotations

from identity_mapper.providers.local_user.domain import LocalUserAccountRecord


class LocalUserAccountDirectory:
    """Read-only local operating system user directory."""

    def get_by_username(self, username: str) -> LocalUserAccountRecord | None:
        try:
            import pwd
        except ImportError:
            return None

        try:
            record = pwd.getpwnam(username)
        except KeyError:
            return None

        return LocalUserAccountRecord(
            username=record.pw_name,
            uid=record.pw_uid,
            gid=record.pw_gid,
            home=record.pw_dir,
            shell=record.pw_shell,
            display_name=record.pw_gecos or None,
        )


class InMemoryLocalUserAccountDirectory:
    """In-memory read-only target directory for local user lookup tests."""

    def __init__(
        self,
        accounts: list[LocalUserAccountRecord] | None = None,
    ) -> None:
        self._by_username: dict[str, LocalUserAccountRecord] = {}

        for account in accounts or []:
            self.add(account)

    def add(self, account: LocalUserAccountRecord) -> None:
        self._by_username[account.username.lower()] = account

    def get_by_username(self, username: str) -> LocalUserAccountRecord | None:
        return self._by_username.get(username.lower())
