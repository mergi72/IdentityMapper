# MapIdentity

`MapIdentity` maps a verified canonical `Identity` into a target identity world.

The capability exists to avoid direct implementation-to-implementation mapping.

```text
Source proof
        |
        v
Source Provider
        |
        v
Identity
        |
        v
Target Mapper
        |
        v
TargetIdentity
```

The source provider validates the source proof and produces `Identity`.

The target mapper receives only:

- the verified `Identity`
- the requested `IdentityTarget`

The target mapper does not receive source credential values and does not call
the source provider.

## Rule

Do not implement:

```text
Kerberos -> AD
```

Implement:

```text
Kerberos proof -> Identity -> AD projection
```

`TargetIdentity` is a projection, not proof that a target account exists.

## Verified Target Worlds

The current target projection suite covers:

- BasicAuth
- Windows / AD
- API Key
- Client Certificate / mTLS
- Federated Identity
- Guest / Anonymous Identity
- LDAP
- Kerberos
- MFA
- OAuth
- Passkeys
- JWT
- SAML
- WebAuthn / FIDO2

Each target mapper implements only:

```text
Identity -> TargetIdentity
```

They do not bind, look up accounts, issue tokens, issue assertions, or verify
target existence. They also do not store credential values, create sessions, or
return runtime connection objects.
