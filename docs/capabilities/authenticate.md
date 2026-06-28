# Authenticate

`Authenticate` orchestrates resolution and verification.

It is the capability that turns an identification plus credential into a
verified identity.

## Contract

```text
Authenticate(Identification, Credential) -> Identity
```

## Flow

```text
Identification
        +
Credential
        |
        v
ResolveIdentity
        |
        v
IdentityCandidate
        |
        v
VerifyCredential
        |
        v
Identity
```

## Rule

Authentication is orchestration. The implementation still maps to the invariant.
