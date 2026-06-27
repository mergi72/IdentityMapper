from identity_mapper_federated.domain import FederatedIdentityRecord


class InMemoryFederatedIdentityStore:
    """In-memory provider for federated identity mappings."""

    def __init__(
        self,
        records: list[FederatedIdentityRecord] | None = None,
    ) -> None:
        self._by_issuer_subject: dict[
            tuple[str, str], FederatedIdentityRecord
        ] = {}
        self._by_trust_mapping_id: dict[str, FederatedIdentityRecord] = {}

        for record in records or []:
            self.add(record)

    def add(self, record: FederatedIdentityRecord) -> None:
        self._by_issuer_subject[
            (record.issuer, record.external_subject)
        ] = record
        self._by_trust_mapping_id[record.trust_mapping_id] = record

    def get_by_issuer_subject(
        self,
        issuer: str,
        external_subject: str,
    ) -> FederatedIdentityRecord | None:
        return self._by_issuer_subject.get((issuer, external_subject))

    def get_by_trust_mapping_id(
        self,
        trust_mapping_id: str,
    ) -> FederatedIdentityRecord | None:
        return self._by_trust_mapping_id.get(trust_mapping_id)
