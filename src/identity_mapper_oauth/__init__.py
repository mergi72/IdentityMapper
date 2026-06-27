"""OAuth reference implementation."""

from identity_mapper_oauth.capabilities import (
    OAuthAuthenticationError,
    OAuthAuthenticator,
    OAuthCredentialVerifier,
    OAuthIdentityResolver,
)
from identity_mapper_oauth.domain import (
    OAuthConfig,
    OAuthTokenRecord,
    OAuthTokenRequest,
)
from identity_mapper_oauth.mapper import (
    OAuthTokenCandidateMapper,
    OAuthTokenIdentityMapper,
    OAuthTokenMapper,
    OAuthTokenResolution,
)
from identity_mapper_oauth.provider import InMemoryOAuthTokenStore

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
