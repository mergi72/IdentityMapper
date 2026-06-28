from identity_mapper.providers.jwt.domain import JwtRecord


class InMemoryJwtStore:
    """In-memory provider for JWT / Bearer Token records."""

    def __init__(self, tokens: list[JwtRecord] | None = None) -> None:
        self._by_subject: dict[str, JwtRecord] = {}
        self._by_jwt_id: dict[str, JwtRecord] = {}

        for token in tokens or []:
            self.add(token)

    def add(self, token: JwtRecord) -> None:
        self._by_subject[token.subject] = token
        self._by_jwt_id[token.jwt_id] = token

    def get_by_subject(self, subject: str) -> JwtRecord | None:
        return self._by_subject.get(subject)

    def get_by_jwt_id(self, jwt_id: str) -> JwtRecord | None:
        return self._by_jwt_id.get(jwt_id)
