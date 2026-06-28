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
  provider
  identification
  credential
```

```text
AuthenticateResponse
  authenticated
  identity
  error
```

## Resolve Identity

```text
ResolveIdentityRequest
  provider
  identification
```

```text
ResolveIdentityResponse
  candidate
  error
```

## Verify Credential

```text
VerifyCredentialRequest
  provider
  candidate
  credential
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
