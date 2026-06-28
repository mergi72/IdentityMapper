# VerifyCredential

`VerifyCredential` verifies that a credential belongs to an identity candidate.

It does not resolve candidates and it does not decide authorization.

## Contract

```text
VerifyCredential(IdentityCandidate, Credential) -> bool
```

## Rule

Verification proves a candidate. It does not define the domain model.
