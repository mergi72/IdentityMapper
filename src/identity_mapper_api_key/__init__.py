"""API Key reference implementation."""

from identity_mapper_api_key.capabilities import (
    ApiKeyAuthenticationError,
    ApiKeyAuthenticator,
    ApiKeyCredentialVerifier,
    ApiKeyIdentityResolver,
)
from identity_mapper_api_key.domain import (
    ApiKeyConfig,
    ApiKeyRecord,
    ApiKeyRequest,
)
from identity_mapper_api_key.mapper import (
    ApiKeyCandidateMapper,
    ApiKeyIdentityMapper,
    ApiKeyMapper,
    ApiKeyResolution,
)
from identity_mapper_api_key.provider import InMemoryApiKeyStore

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
    "InMemoryApiKeyStore",
]
