# Capability Protocol

IdentityMapper capabilities are not tied to HTTP.

A host receives transport-shaped input and turns it into a capability request.
The capability returns a capability response. The host then turns that response
back into transport-shaped output.

```text
Transport Request
        |
        v
Capability Request
        |
        v
Capability
        |
        v
Capability Response
        |
        v
Transport Response
```

## Authenticate

```text
AuthenticateRequest
  identification
  credential
  provider optional
```

```text
AuthenticateResponse
  authenticated
  identity
  error
```

Rejected authentication is represented by the explicit protocol exception:

```text
AuthenticationRejected
```

Host services should treat `AuthenticationRejected` as an authentication
result, not as infrastructure failure.

The public capability response remains:

```text
AuthenticateResponse(authenticated=False)
```

Unexpected provider failures should not be converted into authentication
rejection.

`provider` is a host routing hint, not a domain concept. When it is provided,
the host calls that provider explicitly. When it is omitted, the host may select
a provider according to its registry or policy.

## Resolve Identity

```text
ResolveIdentityRequest
  identification
  provider optional
```

```text
ResolveIdentityResponse
  candidate
  error
```

## Verify Credential

```text
VerifyCredentialRequest
  candidate
  credential
  provider optional
```

```text
VerifyCredentialResponse
  verified
  error
```

## Rule

REST, CLI, gRPC, message bus, and other transports should all reduce to the
same capability request and response contracts.

Transport is a host concern.

Capability protocol is an IdentityMapper contract.

## Source

The primary module for these contracts is:

```text
identity_mapper.capability_protocol
```

`identity_mapper.requests` and `identity_mapper.responses` remain available as
compatibility import surfaces.
