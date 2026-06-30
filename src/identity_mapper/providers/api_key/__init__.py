"""API Key reference implementation."""

from identity_mapper.providers.api_key.capabilities import (
    ApiKeyAuthenticationError,
    ApiKeyAuthenticator,
    ApiKeyCredentialVerifier,
    ApiKeyIdentityResolver,
    ApiKeyTargetIdentityMapper,
)
from identity_mapper.providers.api_key.domain import (
    ApiKeyConfig,
    ApiKeyRecord,
    ApiKeyRequest,
    ApiKeyTargetProjectionConfig,
)
from identity_mapper.providers.api_key.mapper import (
    ApiKeyCandidateMapper,
    ApiKeyIdentityMapper,
    ApiKeyMapper,
    ApiKeyResolution,
)
from identity_mapper.providers.api_key.provider import InMemoryApiKeyStore

__all__ = [
    "ApiKeyAuthenticationError",
    "ApiKeyAuthenticator",
    "ApiKeyCandidateMapper",
    "ApiKeyConfig",
    "ApiKeyCredentialVerifier",
    "ApiKeyIdentityMapper",
    "ApiKeyIdentityResolver",
    "ApiKeyMapper",
    "ApiKeyRecord",
    "ApiKeyRequest",
    "ApiKeyResolution",
    "ApiKeyTargetIdentityMapper",
    "ApiKeyTargetProjectionConfig",
    "InMemoryApiKeyStore",
]
