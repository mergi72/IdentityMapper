"""OAuth reference implementation."""

from identity_mapper.providers.oauth.capabilities import (
    OAuthAuthenticationError,
    OAuthAuthenticator,
    OAuthCredentialVerifier,
    OAuthIdentityResolver,
)
from identity_mapper.providers.oauth.domain import (
    OAuthConfig,
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
    "OAuthTokenCandidateMapper",
    "OAuthTokenIdentityMapper",
    "OAuthTokenMapper",
    "OAuthTokenRecord",
    "OAuthTokenRequest",
    "OAuthTokenResolution",
]
