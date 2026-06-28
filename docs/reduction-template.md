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
  "implementation": "example",
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
| `implementation` | Implementation family described by the template. |
| `invariant` | Domain invariant targeted by the rows. |
| `rows` | Matrix rows. |
| `section` | Domain section for readability. |
| `source` | Implementation field name or path. |
| `literal` | Fixed value mapped into a domain field. |
| `domain` | Target domain field. |

Each row uses either `source` or `literal`.

## Examples

- [BasicAuth](reduction-templates/basic.json)
- [LDAP](reduction-templates/ldap.json)
- [OAuth](reduction-templates/oauth.json)
