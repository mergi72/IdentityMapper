# Credential

`Credential` is the material used to verify an identification.

It can represent a password, token, ticket, assertion, certificate proof,
passkey assertion, API key, or another verification material.

## Fields

| Field | Meaning |
| --- | --- |
| `type` | Credential kind, such as `PASSWORD`, `TOKEN`, `CERTIFICATE`, or `OPAQUE`. |
| `value` | The credential value or proof material. |
| `metadata` | Additional verification context. |

## Role

```text
IdentityCandidate
        +
Credential
        |
        v
VerifyCredential
```

Credential answers:

> Can this candidate be verified?
