from enum import Enum
from dataclasses import dataclass


class SafetyLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SafetyDecisionType(Enum):
    ALLOW = "allow"
    CONFIRM = "confirm"
    DENY = "deny"


@dataclass
class SafetyDecision:
    decision: SafetyDecisionType
    level: SafetyLevel
    reason: str
