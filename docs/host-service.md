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

Response:

```json
{
  "authenticated": true,
  "identity": {
    "id": "identity-1",
    "display_name": "Example Subject"
  }
}
```

## Authenticate Logs

Every `POST /authenticate` request is written to the authenticate request log.

The log is intentionally metadata-only. It records the provider, identifier,
credential type, authentication result, and identity id when authentication
succeeds.

It does not record `credential.value`.

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

JSON response:

```json
{
  "entries": [
    {
      "timestamp": "2026-06-28T12:00:00.000000+00:00",
      "provider": "basic",
      "identifier": "subject",
      "credential_type": "PASSWORD",
      "authenticated": true,
      "status": "accepted",
      "identity_id": "identity-1"
    }
  ]
}
```

Text response:

```text
timestamp                         provider  identifier  credential_type  authenticated  status    identity_id  error
2026-06-28T12:00:00.000000+00:00  basic     subject     PASSWORD         True           accepted  identity-1
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

The service receives transport-shaped input, selects a provider, calls a
capability, and returns transport-shaped output.

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
  "authenticate_log": "logs/authenticate.log"
}
```

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
