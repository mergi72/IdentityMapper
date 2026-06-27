from identity_mapper_saml.domain import SamlAssertionRecord


class InMemorySamlAssertionStore:
    """In-memory provider for SAML assertion records."""

    def __init__(
        self,
        assertions: list[SamlAssertionRecord] | None = None,
    ) -> None:
        self._by_name_id: dict[str, SamlAssertionRecord] = {}
        self._by_assertion_id: dict[str, SamlAssertionRecord] = {}

        for assertion in assertions or []:
            self.add(assertion)

    def add(self, assertion: SamlAssertionRecord) -> None:
        self._by_name_id[assertion.name_id] = assertion
        self._by_assertion_id[assertion.assertion_id] = assertion

    def get_by_name_id(self, name_id: str) -> SamlAssertionRecord | None:
        return self._by_name_id.get(name_id)

    def get_by_assertion_id(
        self,
        assertion_id: str,
    ) -> SamlAssertionRecord | None:
        return self._by_assertion_id.get(assertion_id)
