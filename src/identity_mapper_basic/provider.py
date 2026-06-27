from identity_mapper_basic.domain import BasicUserRecord


class InMemoryBasicUserStore:
    """In-memory provider for basic-auth user records."""

    def __init__(self, users: list[BasicUserRecord] | None = None) -> None:
        self._by_username: dict[str, BasicUserRecord] = {}
        self._by_implementation_id: dict[str, BasicUserRecord] = {}

        for user in users or []:
            self.add(user)

    def add(self, user: BasicUserRecord) -> None:
        self._by_username[user.username] = user
        self._by_implementation_id[user.implementation_id] = user

    def get_by_username(self, username: str) -> BasicUserRecord | None:
        return self._by_username.get(username)

    def get_by_implementation_id(
        self,
        implementation_id: str,
    ) -> BasicUserRecord | None:
        return self._by_implementation_id.get(implementation_id)
