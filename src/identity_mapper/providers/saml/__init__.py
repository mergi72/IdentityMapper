"""SAML reference implementation."""

from identity_mapper.providers.saml.capabilities import (
    SamlAuthenticationError,
    SamlAuthenticator,
    SamlCredentialVerifier,
    SamlIdentityResolver,
)
from identity_mapper.providers.saml.domain import (
    SamlAssertionRecord,
    SamlConfig,
    SamlRequest,
)
from identity_mapper.providers.saml.mapper import (
    SamlCandidateMapper,
    SamlIdentityMapper,
    SamlMapper,
    SamlResolution,
)
from identity_mapper.providers.saml.provider import InMemorySamlAssertionStore

__all__ = [
    "InMemorySamlAssertionStore",
    "SamlAssertionRecord",
    "SamlAuthenticationError",
    "SamlAuthenticator",
    "SamlCandidateMapper",
    "SamlConfig",
    "SamlCredentialVerifier",
    "SamlIdentityMapper",
    "SamlIdentityResolver",
    "SamlMapper",
    "SamlRequest",
    "SamlResolution",
]
