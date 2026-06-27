"""WebAuthn / FIDO2 reference implementation."""

from identity_mapper_webauthn.capabilities import (
    WebAuthnAuthenticationError,
    WebAuthnAuthenticator,
    WebAuthnCredentialVerifier,
    WebAuthnIdentityResolver,
)
from identity_mapper_webauthn.domain import (
    WebAuthnConfig,
    WebAuthnCredentialRecord,
    WebAuthnRequest,
)
from identity_mapper_webauthn.mapper import (
    WebAuthnCandidateMapper,
    WebAuthnIdentityMapper,
    WebAuthnMapper,
    WebAuthnResolution,
)
from identity_mapper_webauthn.provider import InMemoryWebAuthnCredentialStore

__all__ = [
    "InMemoryWebAuthnCredentialStore",
    "WebAuthnAuthenticationError",
    "WebAuthnAuthenticator",
    "WebAuthnCandidateMapper",
    "WebAuthnConfig",
    "WebAuthnCredentialRecord",
    "WebAuthnCredentialVerifier",
    "WebAuthnIdentityMapper",
    "WebAuthnIdentityResolver",
    "WebAuthnMapper",
    "WebAuthnRequest",
    "WebAuthnResolution",
]
