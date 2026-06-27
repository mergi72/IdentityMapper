from identity_mapper_api_key.domain import ApiKeyRecord


class InMemoryApiKeyStore:
    """In-memory provider for API key records."""

    def __init__(self, keys: list[ApiKeyRecord] | None = None) -> None:
        self._by_key_id: dict[str, ApiKeyRecord] = {}

        for key in keys or []:
            self.add(key)

    def add(self, key: ApiKeyRecord) -> None:
        self._by_key_id[key.key_id] = key

    def get_by_key_id(self, key_id: str) -> ApiKeyRecord | None:
        return self._by_key_id.get(key_id)
