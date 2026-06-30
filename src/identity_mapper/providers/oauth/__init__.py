"""OAuth reference implementation."""

from identity_mapper.providers.oauth.capabilities import (
    OAuthAuthenticationError,
    OAuthAuthenticator,
    OAuthCredentialVerifier,
    OAuthIdentityResolver,
    OAuthTargetIdentityMapper,
)
from identity_mapper.providers.oauth.domain import (
    OAuthConfig,
    OAuthTargetProjectionConfig,
    OAuthTokenRecord,
    OAuthTokenRequest,
)
from identity_mapper.providers.oauth.mapper import (
    OAuthTokenCandidateMapper,
    OAuthTokenIdentityMapper,
    OAuthTokenMapper,
    OAuthTokenResolution,
)
from identity_mapper.providers.oauth.provider import InMemoryOAuthTokenStore

__all__ = [
    "InMemoryOAuthTokenStore",
    "OAuthAuthenticationError",
    "OAuthAuthenticator",
    "OAuthConfig",
    "OAuthCredentialVerifier",
    "OAuthIdentityResolver",
    "OAuthTargetIdentityMapper",
    "OAuthTargetProjectionConfig",
    "OAuthTokenCandidateMapper",
    "OAuthTokenIdentityMapper",
    "OAuthTokenMapper",
    "OAuthTokenRecord",
    "OAuthTokenRequest",
    "OAuthTokenResolution",
]
