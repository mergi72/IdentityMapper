"""WebAuthn / FIDO2 reference implementation."""

from identity_mapper.providers.webauthn.capabilities import (
    WebAuthnAuthenticationError,
    WebAuthnAuthenticator,
    WebAuthnCredentialVerifier,
    WebAuthnIdentityResolver,
    WebAuthnTargetIdentityMapper,
)
from identity_mapper.providers.webauthn.domain import (
    WebAuthnConfig,
    WebAuthnCredentialRecord,
    WebAuthnRequest,
    WebAuthnTargetProjectionConfig,
)
from identity_mapper.providers.webauthn.mapper import (
    WebAuthnCandidateMapper,
    WebAuthnIdentityMapper,
    WebAuthnMapper,
    WebAuthnResolution,
)
from identity_mapper.providers.webauthn.provider import InMemoryWebAuthnCredentialStore

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
    "WebAuthnTargetIdentityMapper",
    "WebAuthnTargetProjectionConfig",
]
