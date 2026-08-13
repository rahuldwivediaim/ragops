"""
Access Policy Registry.

Provides runtime lookup of configured access policies.
"""

from __future__ import annotations

from collections.abc import Mapping

from backend.common.config.authorization import AccessPolicyConfig


class AccessPolicyRegistry:
    """
    Registry for configured access policies.

    This registry provides policy-definition lookup only.

    Authorization decisions are handled by the future
    AuthorizationService.
    """

    def __init__(
        self,
        policies: Mapping[str, AccessPolicyConfig],
    ) -> None:
        self._policies = dict(policies)

    def get(
        self,
        policy_id: str,
    ) -> AccessPolicyConfig:
        """
        Return a configured access policy.

        Raises
        ------
        KeyError
            If the policy is not configured.
        """

        try:
            return self._policies[policy_id]
        except KeyError as exc:
            raise KeyError(
                f"Unknown authorization policy: {policy_id}",
            ) from exc

    def exists(
        self,
        policy_id: str,
    ) -> bool:
        """Return whether a policy is configured."""

        return policy_id in self._policies

    def list_ids(self) -> tuple[str, ...]:
        """Return configured policy identifiers."""

        return tuple(self._policies.keys())

    def __len__(self) -> int:
        """Return the number of configured policies."""

        return len(self._policies)


__all__ = ["AccessPolicyRegistry"]
