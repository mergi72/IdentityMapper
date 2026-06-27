from identity_mapper_mfa.domain import MfaRecord


class InMemoryMfaStore:
    """In-memory provider for MFA records."""

    def __init__(self, records: list[MfaRecord] | None = None) -> None:
        self._by_identifier: dict[str, MfaRecord] = {}
        self._by_implementation_id: dict[str, MfaRecord] = {}

        for record in records or []:
            self.add(record)

    def add(self, record: MfaRecord) -> None:
        self._by_identifier[record.identifier] = record
        self._by_implementation_id[record.implementation_id] = record

    def get_by_identifier(self, identifier: str) -> MfaRecord | None:
        return self._by_identifier.get(identifier)

    def get_by_implementation_id(
        self,
        implementation_id: str,
    ) -> MfaRecord | None:
        return self._by_implementation_id.get(implementation_id)
