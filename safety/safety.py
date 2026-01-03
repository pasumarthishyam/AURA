from safety.models import (
    SafetyDecision,
    SafetyDecisionType,
    SafetyLevel
)
from safety.policies import SafetyPolicy
from safety.permissions import PermissionStore


class Safety:
    """
    Evaluates whether an action is safe to execute.
    """

    def __init__(self):
        self.permissions = PermissionStore()

    def _action_key(self, action: dict) -> str:
        return f"{action.get('tool')}:{str(action.get('params'))}"

    def check(self, action: dict) -> SafetyDecision:
        action_key = self._action_key(action)

        # Explicit deny
        if self.permissions.is_denied(action_key):
            return SafetyDecision(
                decision=SafetyDecisionType.DENY,
                level=SafetyLevel.HIGH,
                reason="Action explicitly denied by user"
            )

        # Explicit allow
        if self.permissions.is_allowed(action_key):
            return SafetyDecision(
                decision=SafetyDecisionType.ALLOW,
                level=SafetyLevel.LOW,
                reason="Previously approved action"
            )

        # Classify risk
        level = SafetyPolicy.classify(action)

        if level == SafetyLevel.LOW:
            return SafetyDecision(
                decision=SafetyDecisionType.ALLOW,
                level=level,
                reason="Low-risk action"
            )

        if level == SafetyLevel.MEDIUM:
            return SafetyDecision(
                decision=SafetyDecisionType.CONFIRM,
                level=level,
                reason="Requires user confirmation"
            )

        return SafetyDecision(
            decision=SafetyDecisionType.DENY,
            level=level,
            reason="High-risk action blocked"
        )
