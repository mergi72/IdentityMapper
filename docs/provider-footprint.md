# Provider Footprint

A provider footprint is the provider world's imprint in the domain invariant.

It is represented by the provider-owned `matrix.json` file.

```text
Provider World
      |
      v
Reduction Matrix
      |
      v
Provider Footprint
      |
      v
Domain Invariant
```

## Meaning

A provider has its own model.

For example, an LDAP provider may expose fields such as `uid`, `dn`, `cn`,
`mail`, and `memberOf`.

The footprint declares where those provider-specific fields touch the shared
identity invariant:

```text
uid
        -> Identification.identifier

password
        -> Credential.value

dn
        -> IdentityCandidate.implementation_id

mail
        -> Identity.email
```

This is not authentication logic.

It is a map of invariant points.

## Responsibility

The provider owns its footprint.

The core owns the invariant and the general matrix contract.

```text
core
  owns Identity, Identification, Credential, IdentityCandidate
  owns the ReductionMatrix shape

provider
  owns its implementation model
  owns its matrix.json footprint
```

## Boundary

A footprint does not validate, authenticate, authorize, persist, or decide.

It only declares how the provider model projects into the domain invariant.

The mapper code performs the actual translation. Capabilities perform the
authentication work.
