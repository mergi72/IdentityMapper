from identity_mapper.providers.oauth.domain import OAuthTokenRecord


class InMemoryOAuthTokenStore:
    """In-memory provider for OAuth token records."""

    def __init__(self, tokens: list[OAuthTokenRecord] | None = None) -> None:
        self._by_subject: dict[str, OAuthTokenRecord] = {}
        self._by_token_id: dict[str, OAuthTokenRecord] = {}

        for token in tokens or []:
            self.add(token)

    def add(self, token: OAuthTokenRecord) -> None:
        self._by_subject[token.subject] = token
        self._by_token_id[token.token_id] = token

    def get_by_subject(self, subject: str) -> OAuthTokenRecord | None:
        return self._by_subject.get(subject)

    def get_by_token_id(self, token_id: str) -> OAuthTokenRecord | None:
        return self._by_token_id.get(token_id)
