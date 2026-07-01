import pytest

from identity_mapper.capabilities import Authenticate, MapIdentity, ResolveTargetIdentity
from identity_mapper.capability_protocol import AuthenticationRejected
from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityTarget,
    TargetIdentity,
    TargetIdentityResolution,
)


class ComplianceSourceProvider(Authenticate):
    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        if identification.identifier != "subject":
            raise AuthenticationRejected("unknown subject")
        if credential.type != "COMPLIANCE_PROOF" or credential.value != "accepted":
            raise AuthenticationRejected("invalid proof")
        return Identity(
            id="subject",
            display_name="Compliance Subject",
            roles=("compliance",),
        )


class ComplianceTargetMapper(MapIdentity):
    def map_identity(
        self,
        identity: Identity,
        target: IdentityTarget,
    ) -> TargetIdentity | None:
        if target.provider != "compliance_target":
            return None
        return TargetIdentity(
            identifier=f"compliance_target:{identity.id}",
            target=target,
            attributes={
                "subject_candidate": identity.id,
                "role_hints": tuple(identity.roles),
            },
        )


class ComplianceTargetResolver(ResolveTargetIdentity):
    def resolve_target_identity(
        self,
        target_identity: TargetIdentity,
    ) -> TargetIdentityResolution:
        exists = target_identity.identifier == "compliance_target:subject"
        return TargetIdentityResolution(
            target_identity=target_identity,
            exists=exists,
            attributes={"resolved_by": "compliance"} if exists else {},
        )


def test_source_provider_produces_canonical_identity() -> None:
    identity = ComplianceSourceProvider().authenticate(
        Identification(identifier="subject"),
        Credential(type="COMPLIANCE_PROOF", value="accepted"),
    )

    assert identity == Identity(
        id="subject",
        display_name="Compliance Subject",
        roles=("compliance",),
    )


def test_source_provider_rejects_invalid_proof() -> None:
    with pytest.raises(AuthenticationRejected):
        ComplianceSourceProvider().authenticate(
            Identification(identifier="subject"),
            Credential(type="COMPLIANCE_PROOF", value="wrong"),
        )


def test_target_mapper_consumes_only_identity_and_target_request() -> None:
    identity = Identity(id="subject", roles=("compliance",))
    target = IdentityTarget(provider="compliance_target", realm="test")

    target_identity = ComplianceTargetMapper().map_identity(identity, target)

    assert target_identity == TargetIdentity(
        identifier="compliance_target:subject",
        target=target,
        attributes={
            "subject_candidate": "subject",
            "role_hints": ("compliance",),
        },
    )


def test_target_resolver_consumes_only_target_identity() -> None:
    target_identity = TargetIdentity(
        identifier="compliance_target:subject",
        target=IdentityTarget(provider="compliance_target"),
        attributes={"subject_candidate": "subject"},
    )

    resolution = ComplianceTargetResolver().resolve_target_identity(target_identity)

    assert resolution == TargetIdentityResolution(
        target_identity=target_identity,
        exists=True,
        attributes={"resolved_by": "compliance"},
    )


def test_protocol_flow_keeps_source_and_target_decoupled() -> None:
    identity = ComplianceSourceProvider().authenticate(
        Identification(identifier="subject"),
        Credential(type="COMPLIANCE_PROOF", value="accepted"),
    )
    target_identity = ComplianceTargetMapper().map_identity(
        identity,
        IdentityTarget(provider="compliance_target"),
    )
    assert target_identity is not None

    resolution = ComplianceTargetResolver().resolve_target_identity(target_identity)

    assert resolution.exists
    assert resolution.target_identity is target_identity
