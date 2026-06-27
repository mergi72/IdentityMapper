from identity_mapper_ldap.domain import LdapEntry


class InMemoryLdapDirectory:
    """In-memory provider for LDAP entries."""

    def __init__(self, entries: list[LdapEntry] | None = None) -> None:
        self._by_uid: dict[str, LdapEntry] = {}
        self._by_dn: dict[str, LdapEntry] = {}

        for entry in entries or []:
            self.add(entry)

    def add(self, entry: LdapEntry) -> None:
        self._by_uid[entry.uid] = entry
        self._by_dn[entry.dn] = entry

    def get_by_uid(self, uid: str) -> LdapEntry | None:
        return self._by_uid.get(uid)

    def get_by_dn(self, dn: str) -> LdapEntry | None:
        return self._by_dn.get(dn)
