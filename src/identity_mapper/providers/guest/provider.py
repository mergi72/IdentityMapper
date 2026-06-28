from identity_mapper.providers.guest.domain import GuestSessionRecord


class InMemoryGuestSessionStore:
    """In-memory provider for guest session records."""

    def __init__(
        self,
        sessions: list[GuestSessionRecord] | None = None,
    ) -> None:
        self._by_session_id: dict[str, GuestSessionRecord] = {}

        for session in sessions or []:
            self.add(session)

    def add(self, session: GuestSessionRecord) -> None:
        self._by_session_id[session.session_id] = session

    def get_by_session_id(
        self,
        session_id: str,
    ) -> GuestSessionRecord | None:
        return self._by_session_id.get(session_id)
