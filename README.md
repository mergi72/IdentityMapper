# IdentityMapper

IdentityMapper is the reference implementation of the Invariant Mapping Pattern
for the identity domain.

## The IdentityMapper Rule

Implementations are never mapped to each other.

Every implementation maps only to the domain invariant.

## The Mapper Rule

Mappers never contain business logic.

Their only responsibility is translating implementation models into domain
models.

A mapper does not validate, authenticate, authorize, persist, or decide.

A mapper is deterministic. The same input always produces the same domain
model.

IdentityMapper defines the identity domain model and the capabilities required
to authenticate an identity. It does not perform authentication itself.

## Core Idea

External systems, protocols, products, and APIs have their own implementation
models. A mapper translates one implementation model into a stable domain model.
Business logic works with the domain invariant, not with the implementation.

The Invariant Mapping Pattern is:

```text
Implementation
       |
       v
Mapper
       |
       v
Domain Invariant
       |
       v
Capabilities
```

The pattern can be summarized as:

1. Find the domain invariant.
2. Define the minimal domain contract.
3. Map every implementation to the invariant.
4. Business logic depends only on the invariant.
5. Capabilities extend the invariant.
6. Implementations never communicate directly.

## Why

Without a domain invariant, every implementation must know every other
implementation.

```text
implementation A <-> implementation B
implementation A <-> implementation C
implementation B <-> implementation C
...
```

N implementations require N x (N - 1) direct mappings.

With a domain invariant, every implementation maps only once.

```text
implementation A --+
implementation B --+--> Domain Invariant
implementation C --+
...
```

N implementations require N mappings.

```text
Identification
--------------
identifier

Credential
----------
credential

        |
        v

Authenticate
    |
    +-- ResolveIdentity
    |
    +-- VerifyCredential

        |
        v

Identity
```

`Identification` is not `Identity`.

```text
Identification
--------------
identifier = "subject"

Credential
----------
type = "opaque"
value = "..."

Example credential types include `PASSWORD`, `TOKEN`, `CERTIFICATE`, and
`OPAQUE`. They are examples, not a fixed enum.

Authenticate
------------
verification

Identity
--------
id = "42"
display_name = "Example Subject"
roles = [...]
claims = {...}
attributes = {...}
```

Most authentication systems can be described as two internal operations:

```text
Authenticate
    |
    +-- ResolveIdentity(identification)
    |
    +-- VerifyCredential(candidate, credential)
```

`Authenticate` is the orchestration. `ResolveIdentity` finds the identity
candidate. `VerifyCredential` proves that the credential belongs to that
candidate. Only then does the system produce a verified `Identity`.

An `IdentityCandidate` is not the domain invariant. It represents an
implementation candidate found during resolution:

```text
IdentityCandidate
-----------------
implementation_id = "candidate-42"
identification = Identification(...)
attributes = {...}
```

The verified `Identity.id` is the domain identifier. The candidate's
`implementation_id` is allowed to remain implementation-shaped.

Incorrect:

```text
implementation A -> implementation B
```

Correct:

```text
implementation A -> Identity -> implementation B
```

This keeps implementation details isolated and lets all integrations communicate
through a stable domain invariant.

## BasicAuth Implementation

`identity_mapper_basic` is the first real implementation.

It accepts the smallest useful authentication shape:

```text
user/passwd
```

and maps it to the existing core model:

```text
Identification(username)
Credential(password)
        |
        v
BasicIdentityResolver
BasicCredentialVerifier
        |
        v
Identity
```

The BasicAuth implementation does not change the core domain model or
capability contracts.

## LDAP Implementation

`identity_mapper_ldap` is the second real implementation.

It maps an LDAP bind shape:

```text
uid/password
```

to the same existing core model:

```text
Identification(uid)
Credential(password)
        |
        v
LdapIdentityResolver
LdapCredentialVerifier
        |
        v
Identity
```

The LDAP implementation also leaves the core domain model and capability
contracts unchanged.

## OAuth Implementation

`identity_mapper_oauth` is the third real implementation.

It maps an OAuth token shape:

```text
subject/access_token
```

to the same existing core model:

```text
Identification(subject)
Credential(access_token)
        |
        v
OAuthIdentityResolver
OAuthCredentialVerifier
        |
        v
Identity
```

The OAuth implementation also leaves the core domain model and capability
contracts unchanged.

## API Key Implementation

`identity_mapper_api_key` is the fourth real implementation.

It maps an API key shape:

```text
key_id/api_key
```

to the same existing core model:

```text
Identification(key_id)
Credential(api_key)
        |
        v
ApiKeyIdentityResolver
ApiKeyCredentialVerifier
        |
        v
Identity
```

The API Key implementation also leaves the core domain model and capability
contracts unchanged.

## JWT / Bearer Token Implementation

`identity_mapper_jwt` is the fifth real implementation.

It maps a JWT / Bearer Token shape:

```text
subject/bearer_token
```

to the same existing core model:

```text
Identification(subject)
Credential(bearer_token)
        |
        v
JwtIdentityResolver
JwtCredentialVerifier
        |
        v
Identity
```

The JWT / Bearer Token implementation also leaves the core domain model and
capability contracts unchanged.

## Client Certificate / mTLS Implementation

`identity_mapper_certificate` is the sixth real implementation.

It maps a client certificate shape:

```text
fingerprint/certificate_proof
```

to the same existing core model:

```text
Identification(fingerprint)
Credential(certificate_proof)
        |
        v
ClientCertificateIdentityResolver
ClientCertificateCredentialVerifier
        |
        v
Identity
```

The Client Certificate / mTLS implementation also leaves the core domain model
and capability contracts unchanged.

## Kerberos Implementation

`identity_mapper_kerberos` is the seventh real implementation.

It maps a Kerberos shape:

```text
principal/ticket
```

to the same existing core model:

```text
Identification(principal)
Credential(ticket)
        |
        v
KerberosIdentityResolver
KerberosCredentialVerifier
        |
        v
Identity
```

The Kerberos implementation also leaves the core domain model and capability
contracts unchanged.

## SAML Implementation

`identity_mapper_saml` is the eighth real implementation.

It maps a SAML shape:

```text
name_id/assertion
```

to the same existing core model:

```text
Identification(name_id)
Credential(assertion)
        |
        v
SamlIdentityResolver
SamlCredentialVerifier
        |
        v
Identity
```

The SAML implementation also leaves the core domain model and capability
contracts unchanged.

## Windows / AD SID Implementation

`identity_mapper_windows` is the ninth real implementation.

It maps a Windows identity shape:

```text
sid/logon_proof
```

to the same existing core model:

```text
Identification(sid)
Credential(logon_proof)
        |
        v
WindowsIdentityResolver
WindowsCredentialVerifier
        |
        v
Identity
```

The Windows / AD SID implementation also leaves the core domain model and
capability contracts unchanged.

## Project Scope

IdentityMapper focuses on identity:

- defining `Identification` as the claim used to select an identity candidate
- defining `Credential` as the material used to verify that claim
- defining `Identity` as the verified domain result
- making authentication explicit as identification plus verification
- keeping identity capabilities independent from implementation details

## Project Shape

```text
project:
  IdentityMapper

pattern:
  Invariant Mapping Pattern

core invariant:
  Identity

identification:
  Identification

candidate:
  IdentityCandidate

credential:
  Credential

capabilities:
  Authenticate
  ResolveIdentity
  VerifyCredential
```

## Status

Reference implementation of the Invariant Mapping Pattern under active
development.
