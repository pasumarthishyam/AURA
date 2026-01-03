class PermissionStore:
    """
    Stores user permissions for repeated actions.
    """

    def __init__(self):
        self.allowed = set()
        self.denied = set()

    def is_allowed(self, action_key: str) -> bool:
        return action_key in self.allowed

    def is_denied(self, action_key: str) -> bool:
        return action_key in self.denied

    def allow(self, action_key: str):
        self.allowed.add(action_key)

    def deny(self, action_key: str):
        self.denied.add(action_key)
