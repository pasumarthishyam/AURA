from safety.models import SafetyLevel


class SafetyPolicy:
    """
    Stateless rule-based risk classifier.
    """

    @staticmethod
    def classify(action: dict) -> SafetyLevel:
        tool = action.get("tool", "")
        params = action.get("params", {})

        # File deletion / system modification
        if tool in ["run_shell"] and "rm" in params.get("command", ""):
            return SafetyLevel.HIGH

        # Opening apps / browsers
        if tool in ["open_app", "open_browser"]:
            return SafetyLevel.LOW

        # File writes
        if tool == "write_file":
            return SafetyLevel.MEDIUM

        return SafetyLevel.MEDIUM
