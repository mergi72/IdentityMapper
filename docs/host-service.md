# Host Service

IdentityMapper Host Service is the first runtime host shape.

It is not an auth server.

It exposes IdentityMapper capabilities through HTTP.

```text
Windows Service / Linux daemon
        |
        v
HTTP API / local API
        |
        v
Provider Registry
        |
        v
Provider Capability
```

## Endpoints

The first service surface is intentionally small:

```text
GET  /health
GET  /providers
POST /authenticate
POST /resolve-identity
POST /verify-credential
GET  /authenticate_logs
GET  /audit
```

`/audit` is currently an alias of `/authenticate_logs`.

## Authenticate

HTTP is only the transport.

`POST /authenticate` is translated into `AuthenticateRequest`. The host service
returns `AuthenticateResponse` and then serializes it as HTTP output.

Request:

```json
{
  "provider": "basic",
  "identification": {
    "identifier": "subject"
  },
  "credential": {
    "type": "PASSWORD",
    "value": "accepted"
  }
}
```

`provider` is optional. If it is omitted, the host service asks the provider
registry to select the first provider that accepts the request:

```json
{
  "identification": {
    "identifier": "subject"
  },
  "credential": {
    "type": "PASSWORD",
    "value": "accepted"
  }
}
```

Response:

```json
{
  "authenticated": true,
  "identity": {
    "id": "identity-1",
    "display_name": "Example Subject"
  },
  "error": null
}
```

Rejected response:

```json
{
  "authenticated": false,
  "identity": null,
  "error": null
}
```

Providers signal rejected authentication with `AuthenticationRejected`. The
Host Service converts that signal into `AuthenticateResponse(authenticated=False)`.
Unexpected errors are not treated as authentication rejection.

## Resolve Identity

`POST /resolve-identity` is translated into `ResolveIdentityRequest`.

Request:

```json
{
  "identification": {
    "identifier": "subject"
  }
}
```

Response:

```json
{
  "candidate": {
    "implementation_id": "basic:subject",
    "identification": {
      "identifier": "subject",
      "realm": null,
      "attributes": {}
    },
    "attributes": {
      "source": "basic"
    }
  },
  "error": null
}
```

Unknown identification is a normal capability result:

```json
{
  "candidate": null,
  "error": null
}
```

## Verify Credential

`POST /verify-credential` is translated into `VerifyCredentialRequest`.

Request:

```json
{
  "candidate": {
    "implementation_id": "basic:subject",
    "identification": {
      "identifier": "subject"
    },
    "attributes": {
      "source": "basic"
    }
  },
  "credential": {
    "type": "PASSWORD",
    "value": "accepted"
  }
}
```

Response:

```json
{
  "verified": true,
  "error": null
}
```

Rejected credential verification is also a normal capability result:

```json
{
  "verified": false,
  "error": null
}
```

## Authenticate Logs

Every `POST /authenticate` request is written to the authenticate request log.

The log is intentionally metadata-only. It records the selected provider,
identifier, credential type, authentication result, and identity id when
authentication succeeds.

It does not record `credential.value`.

Timestamps are written using the local timezone configured on the machine
running the Host Service.

Authenticate logging can be disabled in `config/config.json`:

```json
{
  "authenticate_log_enabled": false
}
```

When disabled, no authenticate request log file is written and audit endpoints
return an empty view.

Logs can be read through HTTP:

```text
GET /authenticate_logs
GET /authenticate_logs?limit=20
GET /authenticate_logs?format=json
GET /authenticate_logs?format=text
GET /audit
GET /audit?format=json&limit=20
```

`/audit` is reserved as the more general audit endpoint shape. In the current
service version it exposes the authenticate audit log.

Browser response:

```text
HTML table with a sticky header.
```

The HTML view shows the newest authenticate log entries first so the latest
request is visible directly below the table header.

JSON response:

```json
{
  "entries": [
    {
      "request_id": "3f4a8c71",
      "timestamp": "2026-06-28T12:00:00.000000+00:00",
      "provider": "basic",
      "identifier": "subject",
      "credential_type": "PASSWORD",
      "authenticated": true,
      "status": "accepted",
      "identity_id": "identity-1",
      "duration_ms": 12
    }
  ]
}
```

Text response:

```text
request_id  timestamp                         provider  identifier  credential_type  authenticated  status    identity_id  duration_ms  error
3f4a8c71    2026-06-28T12:00:00.000000+00:00  basic     subject     PASSWORD         True           accepted  identity-1  12
```

The text output is a fixed-width table intended for terminal use.

The HTML view uses a browser meta refresh every 2 seconds so newly received
authentication requests appear without manually reloading the page.

## Boundary

```text
service  = transport + lifecycle
core     = invariant + contracts
provider = implementation + footprint
```

The service must not own the domain model.

The HTTP adapter receives transport-shaped input and maps it to a capability
request.

The host service receives capability requests, selects a provider, calls a
capability, and returns capability responses.

The host service currently exposes the three core identity capabilities:

```text
Authenticate
ResolveIdentity
VerifyCredential
```

Host Service surfaces such as health, provider listing, and audit also return
response objects. The HTTP adapter is responsible for serializing those
responses to transport-shaped output.

## Run

The service can be started as a module:

```text
python -m identity_mapper_service serve
```

By default, the service reads `config/config.json` from the current directory:

```json
{
  "server": "127.0.0.1",
  "port": 8066,
  "max_request_body_bytes": 65536,
  "authenticate_log_enabled": true,
  "authenticate_log": "logs/authenticate.log",
  "authenticate_log_max_entries": 1000
}
```

`max_request_body_bytes` limits HTTP request body size for JSON requests.

`authenticate_log_max_entries` keeps the append-only authenticate audit log
bounded by trimming older entries after writes.

The server and port can still be overridden from the command line:

```text
python -m identity_mapper_service serve --host 127.0.0.1 --port 8066
```

For local experiments, an in-memory Basic provider can be enabled explicitly:

```text
python -m identity_mapper_service serve --demo-basic
```

The host can also be checked from the command line:

```text
python -m identity_mapper_service status
```

Providers can be listed through the running service:

```text
python -m identity_mapper_service providers
```

Authentication can be requested through the running service:

```text
python -m identity_mapper_service authenticate --identifier subject --credential-value accepted
python -m identity_mapper_service authenticate --provider basic --identifier subject --credential-value accepted
python -m identity_mapper_service authenticate --provider basic --identifier subject --credential-value accepted --format json
```

Audit logs can be read through the running service:

```text
python -m identity_mapper_service logs
python -m identity_mapper_service logs --limit 20
python -m identity_mapper_service logs --format json
```
