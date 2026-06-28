from identity_mapper.providers.certificate.domain import ClientCertificateRecord


class InMemoryClientCertificateStore:
    """In-memory provider for client certificate records."""

    def __init__(
        self,
        certificates: list[ClientCertificateRecord] | None = None,
    ) -> None:
        self._by_fingerprint: dict[str, ClientCertificateRecord] = {}

        for certificate in certificates or []:
            self.add(certificate)

    def add(self, certificate: ClientCertificateRecord) -> None:
        self._by_fingerprint[certificate.fingerprint] = certificate

    def get_by_fingerprint(
        self,
        fingerprint: str,
    ) -> ClientCertificateRecord | None:
        return self._by_fingerprint.get(fingerprint)
