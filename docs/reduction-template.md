# Reduction Template

A reduction template is a JSON representation of a reduction matrix.

The JSON file is a provider footprint: it declares how a provider world leaves
an identity-shaped imprint in the domain invariant.

It describes the same sections as the documentation matrix:

```text
identification -> Identification
credential     -> Credential
candidate      -> IdentityCandidate
identity       -> Identity
```

## Scope

The template describes mapping only.

It does not include provider connection settings, credential storage,
authentication flow, authorization rules, persistence, or business decisions.

It does not execute the reduction. Mapper code does that. The template only
names the invariant points.

## Shape

```json
{
  "template": "example",
  "provider": "example",
  "invariant": "Identity",
  "identification": {
    "identifier": "source_field"
  },
  "credential": {
    "type": "PASSWORD",
    "value": "secret_field"
  },
  "candidate": {
    "implementation_id": "provider_id"
  },
  "identity": {
    "id": "identity_id",
    "display_name": "display_name"
  }
}
```

## Fields

| Field | Meaning |
| --- | --- |
| `template` | Template name. |
| `provider` | Provider family described by the template. |
| `invariant` | Domain invariant targeted by the matrix. |
| `identification` | Mapping to `Identification`. |
| `credential` | Mapping to `Credential`. |
| `candidate` | Mapping to `IdentityCandidate`. |
| `identity` | Mapping to `Identity`. |

Values are provider field names or fixed domain values.

The values do not define authentication behavior. They describe where a mapper
can find the data required by the invariant.

## Examples

Provider-owned matrices:

- [BasicAuth](../src/identity_mapper/providers/basic/matrix.json)
- [LDAP](../src/identity_mapper/providers/ldap/matrix.json)
- [OAuth](../src/identity_mapper/providers/oauth/matrix.json)

## Ownership

The core package owns the general matrix contract in `identity_mapper.matrix`.

Each provider owns its concrete `matrix.json`.
