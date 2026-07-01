from identity_mapper.domain import (
    Identity,
    IdentityTarget,
    TargetIdentity,
    TargetIdentityResolution,
)
from identity_mapper.providers.local_user import (
    InMemoryLocalUserAccountDirectory,
    LocalUserAccountRecord,
    LocalUserTargetIdentityMapper,
    LocalUserTargetIdentityResolver,
)


def test_local_user_target_mapper_projects_identity_to_local_user_shape() -> None:
    identity = Identity(
        id="demo@corp.local",
        display_name="Demo User",
        email="demo@corp.local",
        roles=("demo",),
    )
    target = IdentityTarget(provider="local_user", realm="ubuntu")

    target_identity = LocalUserTargetIdentityMapper().map_identity(identity, target)

    assert target_identity == TargetIdentity(
        identifier="local_user:demo",
        target=target,
        attributes={
            "username_candidate": "demo",
            "realm_hint": "ubuntu",
            "display_name_hint": "Demo User",
            "mail_hint": "demo@corp.local",
            "role_hints": ("demo",),
        },
    )


def test_local_user_target_resolver_finds_projected_local_user() -> None:
    target_identity = TargetIdentity(
        identifier="local_user:demo",
        target=IdentityTarget(provider="local_user", realm="ubuntu"),
        attributes={"username_candidate": "demo"},
    )
    directory = InMemoryLocalUserAccountDirectory(
        [
            LocalUserAccountRecord(
                username="demo",
                uid=1001,
                gid=1001,
                home="/home/demo",
                shell="/bin/bash",
                display_name="Demo User",
            )
        ]
    )

    resolution = LocalUserTargetIdentityResolver(directory).resolve_target_identity(
        target_identity
    )

    assert resolution == TargetIdentityResolution(
        target_identity=target_identity,
        exists=True,
        attributes={
            "username": "demo",
            "uid": 1001,
            "gid": 1001,
            "home": "/home/demo",
            "shell": "/bin/bash",
            "display_name": "Demo User",
        },
    )


def test_local_user_target_resolver_returns_not_found_for_missing_local_user() -> None:
    target_identity = TargetIdentity(
        identifier="local_user:missing",
        target=IdentityTarget(provider="local_user", realm="ubuntu"),
        attributes={"username_candidate": "missing"},
    )

    resolution = LocalUserTargetIdentityResolver(
        InMemoryLocalUserAccountDirectory()
    ).resolve_target_identity(target_identity)

    assert resolution == TargetIdentityResolution(
        target_identity=target_identity,
        exists=False,
    )
