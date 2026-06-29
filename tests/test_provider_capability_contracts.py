from dataclasses import dataclass
from typing import Any, Callable

import pytest

from identity_mapper.capabilities import (
    Authenticate,
    MapIdentity,
    ResolveIdentity,
    VerifyCredential,
)
from identity_mapper.capability_protocol import AuthenticationRejected
from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
    IdentityTarget,
    TargetIdentity,
)
from identity_mapper_service.registry import ProviderRegistry
from identity_mapper.providers.api_key import (
    ApiKeyAuthenticator,
    ApiKeyCredentialVerifier,
    ApiKeyIdentityResolver,
    ApiKeyMapper,
    ApiKeyRecord,
    ApiKeyRequest,
    InMemoryApiKeyStore,
)
from identity_mapper.providers.basic import (
    BasicAuthenticationMapper,
    BasicAuthenticationRequest,
    BasicAuthenticator,
    BasicCredentialVerifier,
    BasicIdentityResolver,
    BasicUserRecord,
    InMemoryBasicUserStore,
)
from identity_mapper.providers.certificate import (
    ClientCertificateAuthenticator,
    ClientCertificateCredentialVerifier,
    ClientCertificateIdentityResolver,
    ClientCertificateMapper,
    ClientCertificateRecord,
    ClientCertificateRequest,
    InMemoryClientCertificateStore,
)
from identity_mapper.providers.federated import (
    FederatedAuthenticator,
    FederatedCredentialVerifier,
    FederatedIdentityRecord,
    FederatedIdentityResolver,
    FederatedMapper,
    FederatedRequest,
    InMemoryFederatedIdentityStore,
)
from identity_mapper.providers.guest import (
    GuestAuthenticator,
    GuestCredentialVerifier,
    GuestIdentityResolver,
    GuestMapper,
    GuestRequest,
    GuestSessionRecord,
    InMemoryGuestSessionStore,
)
from identity_mapper.providers.jwt import (
    InMemoryJwtStore,
    JwtAuthenticator,
    JwtCredentialVerifier,
    JwtIdentityResolver,
    JwtMapper,
    JwtRecord,
    JwtRequest,
)
from identity_mapper.providers.kerberos import (
    InMemoryKerberosPrincipalStore,
    KerberosAuthenticator,
    KerberosCredentialVerifier,
    KerberosIdentityResolver,
    KerberosMapper,
    KerberosPrincipalRecord,
    KerberosRequest,
)
from identity_mapper.providers.ldap import (
    InMemoryLdapDirectory,
    LdapAuthenticator,
    LdapBindMapper,
    LdapBindRequest,
    LdapCredentialVerifier,
    LdapEntry,
    LdapIdentityResolver,
)
from identity_mapper.providers.mfa import (
    InMemoryMfaStore,
    MfaAuthenticator,
    MfaCredentialVerifier,
    MfaFactor,
    MfaIdentityResolver,
    MfaMapper,
    MfaRecord,
    MfaRequest,
)
from identity_mapper.providers.oauth import (
    InMemoryOAuthTokenStore,
    OAuthAuthenticator,
    OAuthCredentialVerifier,
    OAuthIdentityResolver,
    OAuthTokenMapper,
    OAuthTokenRecord,
    OAuthTokenRequest,
)
from identity_mapper.providers.passkeys import (
    InMemoryPasskeyStore,
    PasskeyAuthenticator,
    PasskeyCredentialVerifier,
    PasskeyIdentityResolver,
    PasskeyMapper,
    PasskeyRecord,
    PasskeyRequest,
)
from identity_mapper.providers.saml import (
    InMemorySamlAssertionStore,
    SamlAssertionRecord,
    SamlAuthenticator,
    SamlCredentialVerifier,
    SamlIdentityResolver,
    SamlMapper,
    SamlRequest,
)
from identity_mapper.providers.webauthn import (
    InMemoryWebAuthnCredentialStore,
    WebAuthnAuthenticator,
    WebAuthnCredentialRecord,
    WebAuthnCredentialVerifier,
    WebAuthnIdentityResolver,
    WebAuthnMapper,
    WebAuthnRequest,
)
from identity_mapper.providers.windows import (
    InMemoryWindowsIdentityStore,
    WindowsAuthenticator,
    WindowsCredentialVerifier,
    WindowsIdentityRecord,
    WindowsIdentityRequest,
    WindowsIdentityResolver,
    WindowsMapper,
)


@dataclass(frozen=True, slots=True)
class ProviderCapabilityContract:
    name: str
    store_factory: Callable[[], Any]
    mapper_factory: Callable[[], Any]
    resolver_type: type[ResolveIdentity]
    verifier_type: type[VerifyCredential]
    authenticator_type: type[Authenticate]
    valid_request: Any
    invalid_request: Any
    missing_identification: Identification
    expected_candidate: IdentityCandidate
    expected_identity: Identity


def basic_contract() -> ProviderCapabilityContract:
    return ProviderCapabilityContract(
        name="basic",
        store_factory=lambda: InMemoryBasicUserStore(
            [
                BasicUserRecord(
                    implementation_id="basic:subject",
                    username="subject",
                    password="accepted",
                    identity_id="identity-1",
                    display_name="Example Subject",
                    roles=("reader",),
                    claims={"scope": "example"},
                    attributes={"source": "basic"},
                )
            ]
        ),
        mapper_factory=BasicAuthenticationMapper,
        resolver_type=BasicIdentityResolver,
        verifier_type=BasicCredentialVerifier,
        authenticator_type=BasicAuthenticator,
        valid_request=BasicAuthenticationRequest(
            username="subject",
            password="accepted",
        ),
        invalid_request=BasicAuthenticationRequest(
            username="subject",
            password="wrong",
        ),
        missing_identification=Identification(identifier="missing"),
        expected_candidate=IdentityCandidate(
            implementation_id="basic:subject",
            identification=Identification(identifier="subject"),
            attributes={"source": "basic"},
        ),
        expected_identity=Identity(
            id="identity-1",
            display_name="Example Subject",
            roles=("reader",),
            claims={"scope": "example"},
            attributes={"source": "basic"},
        ),
    )


def ldap_contract() -> ProviderCapabilityContract:
    return ProviderCapabilityContract(
        name="ldap",
        store_factory=lambda: InMemoryLdapDirectory(
            [
                LdapEntry(
                    dn="uid=subject,ou=people,dc=example,dc=org",
                    uid="subject",
                    user_password="accepted",
                    identity_id="identity-ldap-1",
                    cn="Example Subject",
                    mail="subject@example.org",
                    groups=("readers",),
                    claims={"directory": "ldap"},
                    attributes={"source": "ldap"},
                )
            ]
        ),
        mapper_factory=LdapBindMapper,
        resolver_type=LdapIdentityResolver,
        verifier_type=LdapCredentialVerifier,
        authenticator_type=LdapAuthenticator,
        valid_request=LdapBindRequest(uid="subject", password="accepted"),
        invalid_request=LdapBindRequest(uid="subject", password="wrong"),
        missing_identification=Identification(identifier="missing"),
        expected_candidate=IdentityCandidate(
            implementation_id="uid=subject,ou=people,dc=example,dc=org",
            identification=Identification(identifier="subject"),
            attributes={"source": "ldap"},
        ),
        expected_identity=Identity(
            id="identity-ldap-1",
            display_name="Example Subject",
            email="subject@example.org",
            roles=("readers",),
            claims={"directory": "ldap"},
            attributes={"source": "ldap"},
        ),
    )


def oauth_contract() -> ProviderCapabilityContract:
    return ProviderCapabilityContract(
        name="oauth",
        store_factory=lambda: InMemoryOAuthTokenStore(
            [
                OAuthTokenRecord(
                    token_id="oauth:token-1",
                    subject="subject",
                    access_token="accepted-token",
                    identity_id="identity-oauth-1",
                    display_name="Example Subject",
                    email="subject@example.org",
                    scopes=("read", "write"),
                    claims={"issuer": "example-idp"},
                    attributes={"source": "oauth"},
                )
            ]
        ),
        mapper_factory=OAuthTokenMapper,
        resolver_type=OAuthIdentityResolver,
        verifier_type=OAuthCredentialVerifier,
        authenticator_type=OAuthAuthenticator,
        valid_request=OAuthTokenRequest(
            subject="subject",
            access_token="accepted-token",
        ),
        invalid_request=OAuthTokenRequest(
            subject="subject",
            access_token="wrong-token",
        ),
        missing_identification=Identification(identifier="missing"),
        expected_candidate=IdentityCandidate(
            implementation_id="oauth:token-1",
            identification=Identification(identifier="subject"),
            attributes={"source": "oauth"},
        ),
        expected_identity=Identity(
            id="identity-oauth-1",
            display_name="Example Subject",
            email="subject@example.org",
            roles=("read", "write"),
            claims={"issuer": "example-idp"},
            attributes={"source": "oauth"},
        ),
    )


def api_key_contract() -> ProviderCapabilityContract:
    return ProviderCapabilityContract(
        name="api-key",
        store_factory=lambda: InMemoryApiKeyStore(
            [
                ApiKeyRecord(
                    key_id="key-1",
                    api_key="accepted-key",
                    identity_id="identity-api-key-1",
                    client_id="client-1",
                    display_name="Example Client",
                    email="client@example.org",
                    roles=("service",),
                    claims={"scope": "payments"},
                    attributes={"source": "api-key"},
                )
            ]
        ),
        mapper_factory=ApiKeyMapper,
        resolver_type=ApiKeyIdentityResolver,
        verifier_type=ApiKeyCredentialVerifier,
        authenticator_type=ApiKeyAuthenticator,
        valid_request=ApiKeyRequest(key_id="key-1", api_key="accepted-key"),
        invalid_request=ApiKeyRequest(key_id="key-1", api_key="wrong-key"),
        missing_identification=Identification(identifier="missing-key"),
        expected_candidate=IdentityCandidate(
            implementation_id="key-1",
            identification=Identification(identifier="key-1"),
            attributes={"source": "api-key"},
        ),
        expected_identity=Identity(
            id="identity-api-key-1",
            display_name="Example Client",
            email="client@example.org",
            roles=("service",),
            claims={"scope": "payments"},
            attributes={"source": "api-key"},
        ),
    )


def certificate_contract() -> ProviderCapabilityContract:
    return ProviderCapabilityContract(
        name="certificate",
        store_factory=lambda: InMemoryClientCertificateStore(
            [
                ClientCertificateRecord(
                    fingerprint="cert:fingerprint-1",
                    proof="accepted-certificate-proof",
                    identity_id="identity-certificate-1",
                    subject="CN=example-client",
                    issuer="CN=example-ca",
                    serial_number="1001",
                    display_name="Example Certificate Client",
                    email="certificate-client@example.org",
                    roles=("service", "mtls"),
                    claims={"certificate": "trusted"},
                    attributes={"source": "client-certificate"},
                )
            ]
        ),
        mapper_factory=ClientCertificateMapper,
        resolver_type=ClientCertificateIdentityResolver,
        verifier_type=ClientCertificateCredentialVerifier,
        authenticator_type=ClientCertificateAuthenticator,
        valid_request=ClientCertificateRequest(
            fingerprint="cert:fingerprint-1",
            proof="accepted-certificate-proof",
        ),
        invalid_request=ClientCertificateRequest(
            fingerprint="cert:fingerprint-1",
            proof="wrong-certificate-proof",
        ),
        missing_identification=Identification(identifier="cert:missing"),
        expected_candidate=IdentityCandidate(
            implementation_id="cert:fingerprint-1",
            identification=Identification(identifier="cert:fingerprint-1"),
            attributes={"source": "client-certificate"},
        ),
        expected_identity=Identity(
            id="identity-certificate-1",
            display_name="Example Certificate Client",
            email="certificate-client@example.org",
            roles=("service", "mtls"),
            claims={"certificate": "trusted"},
            attributes={"source": "client-certificate"},
        ),
    )


def jwt_contract() -> ProviderCapabilityContract:
    return ProviderCapabilityContract(
        name="jwt",
        store_factory=lambda: InMemoryJwtStore(
            [
                JwtRecord(
                    jwt_id="jwt:token-1",
                    subject="subject",
                    bearer_token="accepted-bearer-token",
                    identity_id="identity-jwt-1",
                    display_name="Example Subject",
                    email="subject@example.org",
                    roles=("read", "write"),
                    claims={"scope": "read write"},
                    attributes={"source": "jwt"},
                )
            ]
        ),
        mapper_factory=JwtMapper,
        resolver_type=JwtIdentityResolver,
        verifier_type=JwtCredentialVerifier,
        authenticator_type=JwtAuthenticator,
        valid_request=JwtRequest(
            subject="subject",
            bearer_token="accepted-bearer-token",
        ),
        invalid_request=JwtRequest(
            subject="subject",
            bearer_token="wrong-bearer-token",
        ),
        missing_identification=Identification(identifier="missing"),
        expected_candidate=IdentityCandidate(
            implementation_id="jwt:token-1",
            identification=Identification(identifier="subject"),
            attributes={"source": "jwt"},
        ),
        expected_identity=Identity(
            id="identity-jwt-1",
            display_name="Example Subject",
            email="subject@example.org",
            roles=("read", "write"),
            claims={"scope": "read write"},
            attributes={"source": "jwt"},
        ),
    )


def kerberos_contract() -> ProviderCapabilityContract:
    return ProviderCapabilityContract(
        name="kerberos",
        store_factory=lambda: InMemoryKerberosPrincipalStore(
            [
                KerberosPrincipalRecord(
                    principal="service/example@EXAMPLE.ORG",
                    ticket="accepted-kerberos-ticket",
                    identity_id="identity-kerberos-1",
                    realm="EXAMPLE.ORG",
                    service="service/example",
                    display_name="Example Kerberos Principal",
                    email="kerberos-principal@example.org",
                    roles=("service", "kerberos"),
                    claims={"realm": "EXAMPLE.ORG"},
                    attributes={"source": "kerberos"},
                )
            ]
        ),
        mapper_factory=KerberosMapper,
        resolver_type=KerberosIdentityResolver,
        verifier_type=KerberosCredentialVerifier,
        authenticator_type=KerberosAuthenticator,
        valid_request=KerberosRequest(
            principal="service/example@EXAMPLE.ORG",
            ticket="accepted-kerberos-ticket",
        ),
        invalid_request=KerberosRequest(
            principal="service/example@EXAMPLE.ORG",
            ticket="wrong-kerberos-ticket",
        ),
        missing_identification=Identification(identifier="missing@EXAMPLE.ORG"),
        expected_candidate=IdentityCandidate(
            implementation_id="service/example@EXAMPLE.ORG",
            identification=Identification(identifier="service/example@EXAMPLE.ORG"),
            attributes={"source": "kerberos"},
        ),
        expected_identity=Identity(
            id="identity-kerberos-1",
            display_name="Example Kerberos Principal",
            email="kerberos-principal@example.org",
            roles=("service", "kerberos"),
            claims={"realm": "EXAMPLE.ORG"},
            attributes={"source": "kerberos"},
        ),
    )


def saml_contract() -> ProviderCapabilityContract:
    return ProviderCapabilityContract(
        name="saml",
        store_factory=lambda: InMemorySamlAssertionStore(
            [
                SamlAssertionRecord(
                    assertion_id="saml:assertion-1",
                    name_id="subject@example.org",
                    assertion="accepted-saml-assertion",
                    identity_id="identity-saml-1",
                    display_name="Example SAML Subject",
                    email="subject@example.org",
                    roles=("employee", "saml"),
                    claims={"department": "engineering"},
                    attributes={"source": "saml"},
                )
            ]
        ),
        mapper_factory=SamlMapper,
        resolver_type=SamlIdentityResolver,
        verifier_type=SamlCredentialVerifier,
        authenticator_type=SamlAuthenticator,
        valid_request=SamlRequest(
            name_id="subject@example.org",
            assertion="accepted-saml-assertion",
        ),
        invalid_request=SamlRequest(
            name_id="subject@example.org",
            assertion="wrong-saml-assertion",
        ),
        missing_identification=Identification(identifier="missing@example.org"),
        expected_candidate=IdentityCandidate(
            implementation_id="saml:assertion-1",
            identification=Identification(identifier="subject@example.org"),
            attributes={"source": "saml"},
        ),
        expected_identity=Identity(
            id="identity-saml-1",
            display_name="Example SAML Subject",
            email="subject@example.org",
            roles=("employee", "saml"),
            claims={"department": "engineering"},
            attributes={"source": "saml"},
        ),
    )


def windows_contract() -> ProviderCapabilityContract:
    return ProviderCapabilityContract(
        name="windows",
        store_factory=lambda: InMemoryWindowsIdentityStore(
            [
                WindowsIdentityRecord(
                    sid="S-1-5-21-1000-1001",
                    logon_proof="accepted-windows-logon-proof",
                    identity_id="identity-windows-1",
                    upn="subject@example.org",
                    domain="EXAMPLE",
                    display_name="Example Windows Subject",
                    email="subject@example.org",
                    roles=("employee", "windows"),
                    claims={"domain": "EXAMPLE"},
                    attributes={"source": "windows"},
                )
            ]
        ),
        mapper_factory=WindowsMapper,
        resolver_type=WindowsIdentityResolver,
        verifier_type=WindowsCredentialVerifier,
        authenticator_type=WindowsAuthenticator,
        valid_request=WindowsIdentityRequest(
            sid="S-1-5-21-1000-1001",
            logon_proof="accepted-windows-logon-proof",
        ),
        invalid_request=WindowsIdentityRequest(
            sid="S-1-5-21-1000-1001",
            logon_proof="wrong-windows-logon-proof",
        ),
        missing_identification=Identification(identifier="S-1-5-21-1000-4040"),
        expected_candidate=IdentityCandidate(
            implementation_id="S-1-5-21-1000-1001",
            identification=Identification(identifier="S-1-5-21-1000-1001"),
            attributes={"source": "windows"},
        ),
        expected_identity=Identity(
            id="identity-windows-1",
            display_name="Example Windows Subject",
            email="subject@example.org",
            roles=("employee", "windows"),
            claims={"domain": "EXAMPLE"},
            attributes={"source": "windows"},
        ),
    )


def webauthn_contract() -> ProviderCapabilityContract:
    return ProviderCapabilityContract(
        name="webauthn",
        store_factory=lambda: InMemoryWebAuthnCredentialStore(
            [
                WebAuthnCredentialRecord(
                    credential_id="webauthn:credential-1",
                    assertion="accepted-webauthn-assertion",
                    identity_id="identity-webauthn-1",
                    user_handle="user-handle-1",
                    relying_party_id="example.org",
                    display_name="Example WebAuthn Subject",
                    email="subject@example.org",
                    roles=("employee", "webauthn"),
                    claims={"authenticator": "platform"},
                    attributes={"source": "webauthn"},
                )
            ]
        ),
        mapper_factory=WebAuthnMapper,
        resolver_type=WebAuthnIdentityResolver,
        verifier_type=WebAuthnCredentialVerifier,
        authenticator_type=WebAuthnAuthenticator,
        valid_request=WebAuthnRequest(
            credential_id="webauthn:credential-1",
            assertion="accepted-webauthn-assertion",
        ),
        invalid_request=WebAuthnRequest(
            credential_id="webauthn:credential-1",
            assertion="wrong-webauthn-assertion",
        ),
        missing_identification=Identification(identifier="webauthn:missing"),
        expected_candidate=IdentityCandidate(
            implementation_id="webauthn:credential-1",
            identification=Identification(identifier="webauthn:credential-1"),
            attributes={"source": "webauthn"},
        ),
        expected_identity=Identity(
            id="identity-webauthn-1",
            display_name="Example WebAuthn Subject",
            email="subject@example.org",
            roles=("employee", "webauthn"),
            claims={"authenticator": "platform"},
            attributes={"source": "webauthn"},
        ),
    )


def passkeys_contract() -> ProviderCapabilityContract:
    return ProviderCapabilityContract(
        name="passkeys",
        store_factory=lambda: InMemoryPasskeyStore(
            [
                PasskeyRecord(
                    passkey_id="passkey:credential-1",
                    assertion="accepted-passkey-assertion",
                    identity_id="identity-passkey-1",
                    user_handle="user-handle-1",
                    relying_party_id="example.org",
                    device_name="Example Device",
                    display_name="Example Passkey Subject",
                    email="subject@example.org",
                    roles=("employee", "passkey"),
                    claims={"authenticator": "synced-passkey"},
                    attributes={"source": "passkeys"},
                )
            ]
        ),
        mapper_factory=PasskeyMapper,
        resolver_type=PasskeyIdentityResolver,
        verifier_type=PasskeyCredentialVerifier,
        authenticator_type=PasskeyAuthenticator,
        valid_request=PasskeyRequest(
            passkey_id="passkey:credential-1",
            assertion="accepted-passkey-assertion",
        ),
        invalid_request=PasskeyRequest(
            passkey_id="passkey:credential-1",
            assertion="wrong-passkey-assertion",
        ),
        missing_identification=Identification(identifier="passkey:missing"),
        expected_candidate=IdentityCandidate(
            implementation_id="passkey:credential-1",
            identification=Identification(identifier="passkey:credential-1"),
            attributes={"source": "passkeys"},
        ),
        expected_identity=Identity(
            id="identity-passkey-1",
            display_name="Example Passkey Subject",
            email="subject@example.org",
            roles=("employee", "passkey"),
            claims={"authenticator": "synced-passkey"},
            attributes={"source": "passkeys"},
        ),
    )


def mfa_contract() -> ProviderCapabilityContract:
    valid_request = MfaRequest(
        identifier="subject",
        factors=(
            MfaFactor(type="PASSWORD", value="accepted-password"),
            MfaFactor(type="TOTP", value="123456"),
        ),
    )
    invalid_request = MfaRequest(
        identifier="subject",
        factors=(
            MfaFactor(type="PASSWORD", value="accepted-password"),
            MfaFactor(type="TOTP", value="000000"),
        ),
    )
    return ProviderCapabilityContract(
        name="mfa",
        store_factory=lambda: InMemoryMfaStore(
            [
                MfaRecord(
                    implementation_id="mfa:subject",
                    identifier="subject",
                    required_factors={
                        "PASSWORD": "accepted-password",
                        "TOTP": "123456",
                    },
                    identity_id="identity-mfa-1",
                    display_name="Example MFA Subject",
                    email="subject@example.org",
                    roles=("employee", "mfa"),
                    claims={"assurance": "multi-factor"},
                    attributes={"source": "mfa"},
                )
            ]
        ),
        mapper_factory=MfaMapper,
        resolver_type=MfaIdentityResolver,
        verifier_type=MfaCredentialVerifier,
        authenticator_type=MfaAuthenticator,
        valid_request=valid_request,
        invalid_request=invalid_request,
        missing_identification=Identification(identifier="missing"),
        expected_candidate=IdentityCandidate(
            implementation_id="mfa:subject",
            identification=Identification(identifier="subject"),
            attributes={"source": "mfa"},
        ),
        expected_identity=Identity(
            id="identity-mfa-1",
            display_name="Example MFA Subject",
            email="subject@example.org",
            roles=("employee", "mfa"),
            claims={"assurance": "multi-factor"},
            attributes={"source": "mfa"},
        ),
    )


def federated_contract() -> ProviderCapabilityContract:
    return ProviderCapabilityContract(
        name="federated",
        store_factory=lambda: InMemoryFederatedIdentityStore(
            [
                FederatedIdentityRecord(
                    trust_mapping_id="federation:subject",
                    issuer="example-idp",
                    external_subject="external-subject",
                    assertion="accepted-federation-assertion",
                    identity_id="identity-federated-1",
                    audience="example-app",
                    display_name="Example Federated Subject",
                    email="subject@example.org",
                    roles=("employee", "federated"),
                    claims={"issuer": "example-idp"},
                    attributes={"source": "federated"},
                )
            ]
        ),
        mapper_factory=FederatedMapper,
        resolver_type=FederatedIdentityResolver,
        verifier_type=FederatedCredentialVerifier,
        authenticator_type=FederatedAuthenticator,
        valid_request=FederatedRequest(
            issuer="example-idp",
            external_subject="external-subject",
            assertion="accepted-federation-assertion",
        ),
        invalid_request=FederatedRequest(
            issuer="example-idp",
            external_subject="external-subject",
            assertion="wrong-federation-assertion",
        ),
        missing_identification=Identification(
            identifier="missing-subject",
            realm="example-idp",
        ),
        expected_candidate=IdentityCandidate(
            implementation_id="federation:subject",
            identification=Identification(
                identifier="external-subject",
                realm="example-idp",
                attributes={"issuer": "example-idp"},
            ),
            attributes={"source": "federated"},
        ),
        expected_identity=Identity(
            id="identity-federated-1",
            display_name="Example Federated Subject",
            email="subject@example.org",
            roles=("employee", "federated"),
            claims={"issuer": "example-idp"},
            attributes={"source": "federated"},
        ),
    )


def guest_contract() -> ProviderCapabilityContract:
    return ProviderCapabilityContract(
        name="guest",
        store_factory=lambda: InMemoryGuestSessionStore(
            [
                GuestSessionRecord(
                    session_id="guest-session-1",
                    session_token="accepted-guest-token",
                    identity_id="identity-guest-1",
                    claims={"anonymous": True},
                    attributes={"source": "guest"},
                )
            ]
        ),
        mapper_factory=GuestMapper,
        resolver_type=GuestIdentityResolver,
        verifier_type=GuestCredentialVerifier,
        authenticator_type=GuestAuthenticator,
        valid_request=GuestRequest(
            session_id="guest-session-1",
            session_token="accepted-guest-token",
        ),
        invalid_request=GuestRequest(
            session_id="guest-session-1",
            session_token="wrong-guest-token",
        ),
        missing_identification=Identification(identifier="missing-guest-session"),
        expected_candidate=IdentityCandidate(
            implementation_id="guest-session-1",
            identification=Identification(
                identifier="guest-session-1",
                realm="guest",
                attributes={"kind": "guest"},
            ),
            attributes={"source": "guest"},
        ),
        expected_identity=Identity(
            id="identity-guest-1",
            display_name="Guest",
            roles=("guest",),
            claims={"anonymous": True},
            attributes={"source": "guest"},
        ),
    )


CONTRACTS = (
    basic_contract(),
    ldap_contract(),
    oauth_contract(),
    api_key_contract(),
    jwt_contract(),
    certificate_contract(),
    kerberos_contract(),
    saml_contract(),
    windows_contract(),
    webauthn_contract(),
    passkeys_contract(),
    mfa_contract(),
    federated_contract(),
    guest_contract(),
)


def contract_ids(contract: ProviderCapabilityContract) -> str:
    return contract.name


class ContractTargetIdentityMapper(MapIdentity):
    def __init__(self, provider: str) -> None:
        self.provider = provider
        self.calls = 0

    def map_identity(
        self,
        identity: Identity,
        target: IdentityTarget,
    ) -> TargetIdentity | None:
        self.calls += 1
        if target.provider != self.provider:
            return None

        return TargetIdentity(
            identifier=f"{self.provider}:{identity.id}",
            target=target,
            attributes={"source": self.provider},
        )


def registry_with_all_provider_authenticators_and_target_mappers(
) -> tuple[ProviderRegistry, dict[str, ContractTargetIdentityMapper]]:
    registry = ProviderRegistry()
    target_mappers: dict[str, ContractTargetIdentityMapper] = {}

    for contract in CONTRACTS:
        registry.register_authenticator(
            contract.name,
            contract.authenticator_type(contract.store_factory()),
        )
        target_mapper = ContractTargetIdentityMapper(contract.name)
        registry.register_identity_mapper(contract.name, target_mapper)
        target_mappers[contract.name] = target_mapper

    return registry, target_mappers


PROVIDER_MAPPING_CONTRACTS = tuple(
    pytest.param(
        source_contract,
        target_contract,
        id=f"{source_contract.name}->{target_contract.name}",
    )
    for source_contract in CONTRACTS
    for target_contract in CONTRACTS
)


@pytest.mark.parametrize("contract", CONTRACTS, ids=contract_ids)
def test_provider_mapper_returns_identity_inputs(
    contract: ProviderCapabilityContract,
) -> None:
    identification, credential = contract.mapper_factory().to_domain(
        contract.valid_request
    )

    assert isinstance(identification, Identification)
    assert isinstance(credential, Credential)


@pytest.mark.parametrize("contract", CONTRACTS, ids=contract_ids)
def test_provider_resolver_returns_candidate_not_identity(
    contract: ProviderCapabilityContract,
) -> None:
    identification, _ = contract.mapper_factory().to_domain(
        contract.valid_request
    )

    candidate = contract.resolver_type(
        contract.store_factory()
    ).resolve_identity(identification)

    assert candidate == contract.expected_candidate
    assert isinstance(candidate, IdentityCandidate)
    assert not isinstance(candidate, Identity)


@pytest.mark.parametrize("contract", CONTRACTS, ids=contract_ids)
def test_provider_resolver_returns_none_for_unknown_identification(
    contract: ProviderCapabilityContract,
) -> None:
    candidate = contract.resolver_type(
        contract.store_factory()
    ).resolve_identity(contract.missing_identification)

    assert candidate is None


@pytest.mark.parametrize("contract", CONTRACTS, ids=contract_ids)
def test_provider_verifier_accepts_valid_credential(
    contract: ProviderCapabilityContract,
) -> None:
    _, credential = contract.mapper_factory().to_domain(contract.valid_request)

    assert contract.verifier_type(contract.store_factory()).verify_credential(
        contract.expected_candidate,
        credential,
    )


@pytest.mark.parametrize("contract", CONTRACTS, ids=contract_ids)
def test_provider_verifier_rejects_invalid_credential(
    contract: ProviderCapabilityContract,
) -> None:
    _, credential = contract.mapper_factory().to_domain(contract.invalid_request)

    assert not contract.verifier_type(
        contract.store_factory()
    ).verify_credential(
        contract.expected_candidate,
        credential,
    )


@pytest.mark.parametrize("contract", CONTRACTS, ids=contract_ids)
def test_provider_authenticator_returns_identity(
    contract: ProviderCapabilityContract,
) -> None:
    identification, credential = contract.mapper_factory().to_domain(
        contract.valid_request
    )

    identity = contract.authenticator_type(contract.store_factory()).authenticate(
        identification,
        credential,
    )

    assert identity == contract.expected_identity


@pytest.mark.parametrize("contract", CONTRACTS, ids=contract_ids)
def test_provider_authenticator_rejects_invalid_credential(
    contract: ProviderCapabilityContract,
) -> None:
    identification, credential = contract.mapper_factory().to_domain(
        contract.invalid_request
    )

    with pytest.raises(AuthenticationRejected):
        contract.authenticator_type(contract.store_factory()).authenticate(
            identification,
            credential,
        )


@pytest.mark.parametrize(
    ("source_contract", "target_contract"),
    PROVIDER_MAPPING_CONTRACTS,
)
def test_provider_identity_can_map_to_every_target_provider_through_verified_identity(
    source_contract: ProviderCapabilityContract,
    target_contract: ProviderCapabilityContract,
) -> None:
    registry, target_mappers = registry_with_all_provider_authenticators_and_target_mappers()
    source_identification, source_credential = (
        source_contract.mapper_factory().to_domain(source_contract.valid_request)
    )

    result = registry.map_identity(
        source_provider=source_contract.name,
        identification=source_identification,
        credential=source_credential,
        target=IdentityTarget(
            provider=target_contract.name,
            purpose="contract",
        ),
    )

    assert result.source_provider == source_contract.name
    assert result.target_provider == target_contract.name
    assert result.identity == source_contract.expected_identity
    assert result.target_identity == TargetIdentity(
        identifier=f"{target_contract.name}:{source_contract.expected_identity.id}",
        target=IdentityTarget(
            provider=target_contract.name,
            purpose="contract",
        ),
        attributes={"source": target_contract.name},
    )
    assert target_mappers[target_contract.name].calls == 1


@pytest.mark.parametrize("contract", CONTRACTS, ids=contract_ids)
def test_provider_identity_mapping_does_not_call_target_without_verified_identity(
    contract: ProviderCapabilityContract,
) -> None:
    registry, target_mappers = registry_with_all_provider_authenticators_and_target_mappers()
    source_identification, source_credential = (
        contract.mapper_factory().to_domain(contract.invalid_request)
    )

    with pytest.raises(AuthenticationRejected):
        registry.map_identity(
            source_provider=contract.name,
            identification=source_identification,
            credential=source_credential,
            target=IdentityTarget(
                provider=contract.name,
                purpose="self",
            ),
        )

    assert target_mappers[contract.name].calls == 0
