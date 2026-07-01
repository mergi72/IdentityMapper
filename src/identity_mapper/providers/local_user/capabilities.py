from identity_mapper.capabilities import MapIdentity, ResolveTargetIdentity
from identity_mapper.domain import (
    Identity,
    IdentityTarget,
    TargetIdentity,
    TargetIdentityResolution,
)
from identity_mapper.providers.local_user.domain import (
    LocalUserAccountRecord,
    LocalUserTargetProjectionConfig,
)
from identity_mapper.providers.local_user.provider import (
    InMemoryLocalUserAccountDirectory,
    LocalUserAccountDirectory,
)


class LocalUserTargetIdentityMapper(MapIdentity):
    """Projects a verified Identity into a local OS user target identity shape."""

    def __init__(
        self,
        config: LocalUserTargetProjectionConfig | None = None,
    ) -> None:
        self._config = config or LocalUserTargetProjectionConfig()

    def map_identity(
        self,
        identity: Identity,
        target: IdentityTarget,
    ) -> TargetIdentity | None:
        if target.provider != self._config.provider:
            return None

        username_candidate = identity.id.split("@", 1)[0].split("\\")[-1]
        realm = target.realm or self._config.default_realm
        return TargetIdentity(
            identifier=f"{target.provider}:{username_candidate}",
            target=target,
            attributes={
                key: value
                for key, value in {
                    "username_candidate": username_candidate,
                    "realm_hint": realm,
                    "display_name_hint": identity.display_name,
                    "mail_hint": identity.email,
                    "role_hints": tuple(identity.roles),
                }.items()
                if value is not None
            },
        )


class LocalUserTargetIdentityResolver(ResolveTargetIdentity):
    """Looks up a local OS user target identity projection."""

    def __init__(
        self,
        directory: LocalUserAccountDirectory | InMemoryLocalUserAccountDirectory,
        config: LocalUserTargetProjectionConfig | None = None,
    ) -> None:
        self._directory = directory
        self._config = config or LocalUserTargetProjectionConfig()

    def resolve_target_identity(
        self,
        target_identity: TargetIdentity,
    ) -> TargetIdentityResolution:
        if target_identity.target.provider != self._config.provider:
            return TargetIdentityResolution(
                target_identity=target_identity,
                exists=False,
            )

        username = target_identity.attributes.get("username_candidate")
        if not isinstance(username, str):
            return TargetIdentityResolution(
                target_identity=target_identity,
                exists=False,
            )

        account = self._directory.get_by_username(username)
        if account is None:
            return TargetIdentityResolution(
                target_identity=target_identity,
                exists=False,
            )

        return TargetIdentityResolution(
            target_identity=target_identity,
            exists=True,
            attributes=self._account_attributes(account),
        )

    def _account_attributes(
        self,
        account: LocalUserAccountRecord,
    ) -> dict[str, object]:
        return {
            key: value
            for key, value in {
                "username": account.username,
                "uid": account.uid,
                "gid": account.gid,
                "home": account.home,
                "shell": account.shell,
                "display_name": account.display_name,
                **account.attributes,
            }.items()
            if value is not None
        }
