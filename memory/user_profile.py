import json
import os


class UserProfileMemory:
    """
    Structured memory about the user.
    This is NOT vectorized.
    """

    def __init__(self, path: str = "./user_profile.json"):
        self.path = path
        self.profile = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "preferences": {},
            "habits": {},
            "risk_tolerance": {},
            "style": {},
        }

    def update(self, section: str, key: str, value):
        if section not in self.profile:
            self.profile[section] = {}

        self.profile[section][key] = value
        self._save()

    def get_profile(self) -> dict:
        return self.profile

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.profile, f, indent=2)
