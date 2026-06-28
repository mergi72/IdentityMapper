# Reduction Template

A reduction template is a JSON representation of a reduction matrix.

It describes the same rows as the documentation matrix:

```text
Implementation field -> Domain field
Literal value        -> Domain field
```

## Scope

The template describes mapping only.

It does not include provider connection settings, credential storage,
authentication flow, authorization rules, persistence, or business decisions.

## Shape

```json
{
  "template": "example",
  "provider": "example",
  "invariant": "Identity",
  "rows": [
    {
      "section": "Identification",
      "source": "source_field",
      "domain": "Identification.identifier"
    },
    {
      "section": "Credential",
      "literal": "PASSWORD",
      "domain": "Credential.type"
    }
  ]
}
```

## Fields

| Field | Meaning |
| --- | --- |
| `template` | Template name. |
| `provider` | Provider family described by the template. |
| `invariant` | Domain invariant targeted by the rows. |
| `rows` | Matrix rows. |
| `section` | Domain section for readability. |
| `source` | Implementation field name or path. |
| `literal` | Fixed value mapped into a domain field. |
| `domain` | Target domain field. |

Each row uses either `source` or `literal`.

## Examples

Provider-owned matrices:

- [BasicAuth](../src/identity_mapper/providers/basic/matrix.json)
- [LDAP](../src/identity_mapper/providers/ldap/matrix.json)
- [OAuth](../src/identity_mapper/providers/oauth/matrix.json)

## Ownership

The core package owns the general matrix contract in `identity_mapper.matrix`.

Each provider owns its concrete `matrix.json`.
