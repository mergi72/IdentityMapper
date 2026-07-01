# External Implementation Experiment

This experiment tests whether IdentityMapper Protocol can be implemented from
the specification documents without reading the Python reference source code.

It is not a production integration test.

It is a protocol documentation test.

## Goal

Verify this statement:

```text
A compatible implementation can be written without reading the Python source
code.
```

## Participant Rule

The implementer may read:

- [RFC 0001: IdentityMapper Protocol](rfcs/0001-identitymapper-protocol.md)
- [RFC 0002: IdentityMapper Compliance Suite](rfcs/0002-compliance-suite.md)
- [RFC 0003: IdentityMapper Protocol Versioning](rfcs/0003-protocol-versioning.md)
- [Implementer's guide](implementers-guide.md)
- [Compliance badge](compliance-badge.md)
- [Compliance suite README](../compliance/README.md)

The implementer must not read:

```text
src/
tests/
```

The point is to test whether the protocol documents are sufficient.

## Task

Write a minimal compatible implementation with:

```text
FakeToken Source Provider
Demo Target Identity Mapper
Demo Target Identity Resolver
```

The implementation language is not prescribed.

Python, Go, C#, Java, Rust, JavaScript, or any other language is acceptable.

## Required Source Provider

Name:

```text
FakeToken Source Provider
```

Input:

```text
Identification.identifier
Credential.type
Credential.value
```

Valid proof:

```text
identifier = "demo"
credential.type = "FAKE_TOKEN"
credential.value = "valid-demo-token"
```

Expected output:

```text
Identity
```

with at least:

```text
id = "demo"
display_name = "Demo User"
roles = ["demo"]
attributes.source = "fake-token"
```

Invalid proof must be rejected and must not produce `Identity`.

## Required Target Identity Mapper

Name:

```text
Demo Target Identity Mapper
```

Input:

```text
Identity
Target request
```

Expected output:

```text
TargetIdentity
```

with at least:

```text
identifier = "demo-target:demo"
target.provider = "demo_target"
target.realm = "experiment"
target.purpose = "protocol_test"
attributes.username_candidate = "demo"
attributes.display_name_hint = "Demo User"
```

The target mapper must not receive credential values.

The target mapper must not confirm account existence.

## Required Target Identity Resolver

Name:

```text
Demo Target Identity Resolver
```

Input:

```text
TargetIdentity
```

Expected output:

```text
TargetIdentityResolution
```

For:

```text
TargetIdentity.identifier = "demo-target:demo"
```

the resolver should return:

```text
resolved = true
exists = true
attributes.username = "demo"
```

For any other target identity, the resolver should return a negative
resolution.

The resolver must not receive source credential values.

## Required Flow

The implementation must demonstrate:

```text
Identification + Credential
        |
        v
FakeToken Source Provider
        |
        v
Identity
        |
        v
Demo Target Identity Mapper
        |
        v
TargetIdentity
        |
        v
Demo Target Identity Resolver
        |
        v
TargetIdentityResolution
```

## Required Tests

The implementer should provide tests proving:

- valid source proof produces canonical `Identity`
- invalid source proof is rejected
- target mapper consumes `Identity`
- target mapper produces `TargetIdentity`
- target mapper does not receive credential values
- target resolver consumes `TargetIdentity`
- target resolver produces `TargetIdentityResolution`
- target resolver does not receive credential values
- source provider does not know the target mapper
- target mapper does not know the source provider
- source and target do not communicate directly

## Forbidden Shortcuts

The implementation fails the experiment if it:

- maps fake token directly to target identity
- passes credential value to target mapper
- passes credential value to target resolver
- stores credential value in logs, files, cache, or database
- treats `TargetIdentity` projection as account verification
- performs login, bind, session creation, or authorization
- requires reading the Python reference implementation to complete the task

## Expected Report

The implementer should report:

```text
implementation: <name> <version>
language: <language>
protocol: IdentityMapper Protocol 1.0 Draft
result: pass/fail
tests: <summary>
source_read: yes/no
notes: <short notes>
```

## Success Criteria

The experiment succeeds if a person can implement the required flow by reading
only the allowed documents.

The experiment fails if the person must inspect the Python source code to
understand the protocol boundary.

