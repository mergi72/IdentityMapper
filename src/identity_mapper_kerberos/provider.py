from identity_mapper_kerberos.domain import KerberosPrincipalRecord


class InMemoryKerberosPrincipalStore:
    """In-memory provider for Kerberos principal records."""

    def __init__(
        self,
        principals: list[KerberosPrincipalRecord] | None = None,
    ) -> None:
        self._by_principal: dict[str, KerberosPrincipalRecord] = {}

        for principal in principals or []:
            self.add(principal)

    def add(self, principal: KerberosPrincipalRecord) -> None:
        self._by_principal[principal.principal] = principal

    def get_by_principal(
        self,
        principal: str,
    ) -> KerberosPrincipalRecord | None:
        return self._by_principal.get(principal)
