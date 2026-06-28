# Reduction Matrix

The reduction matrix is a documentation table.

It shows how implementation-specific identity models reduce to the same core
domain invariant.

```text
Implementation
       |
       v
Identification + Credential
       |
       v
IdentityCandidate
       |
       v
Identity
```

## Overview

| Version | Provider | Identification | Credential | Candidate | Details |
| --- | --- | --- | --- | --- | --- |
| v0.2.0 | BasicAuth | username | password | user record | [basic](providers/basic.md) |
| v0.3.0 | LDAP | uid | password | LDAP entry | [ldap](providers/ldap.md) |
| v0.4.0 | OAuth | subject/client | token/secret | OAuth principal | [oauth](providers/oauth.md) |
| v0.5.0 | API Key | key id | API key | key record | [api-key](providers/api-key.md) |
| v0.6.0 | JWT / Bearer Token | subject/issuer | bearer token | token claims | [jwt](providers/jwt.md) |
| v0.7.0 | Client Certificate / mTLS | certificate subject | certificate proof | certificate record | [certificate](providers/certificate.md) |
| v0.8.0 | Kerberos | principal | ticket | principal record | [kerberos](providers/kerberos.md) |
| v0.9.0 | SAML | NameID/issuer | assertion | SAML subject | [saml](providers/saml.md) |
| v0.10.0 | Windows / AD SID | SID/UPN | logon token | Windows account | [windows](providers/windows.md) |
| v0.12.0 | WebAuthn / FIDO2 | credential id/user handle | authenticator assertion | authenticator credential | [webauthn](providers/webauthn.md) |
| v0.13.0 | Passkeys | passkey id/user handle | passkey assertion | passkey record | [passkeys](providers/passkeys.md) |
| v0.14.0 | MFA | challenge/session | factor proofs | MFA session | [mfa](providers/mfa.md) |
| v0.15.0 | Federated Identity | external subject/issuer | federation assertion | trust mapping | [federated](providers/federated.md) |
| v0.16.0 | Guest / Anonymous Identity | session id | guest session token | guest session | [guest](providers/guest.md) |

## Purpose

The matrix answers one question:

> Can this implementation be reduced to the identity invariant without changing
> the core model?

For all listed implementations, the answer is yes.

## Template

A reduction template is the same matrix written as JSON rows.

See [Reduction Template](reduction-template.md).

Concrete JSON matrices live with their providers, for example
`src/identity_mapper/providers/ldap/matrix.json`.
