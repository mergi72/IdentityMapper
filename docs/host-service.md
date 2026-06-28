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
```

## Authenticate

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
  "port": 8066
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
