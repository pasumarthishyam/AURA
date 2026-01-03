from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.user_profile import UserProfileMemory


class MemorySystem:
    """
    Unified memory interface used by the Core Agent Controller.
    """

    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.user_profile = UserProfileMemory()

    # -------------------------------------------------
    # Called ONCE at task start by controller
    # -------------------------------------------------

    def retrieve(self, goal: str) -> str:
        """
        Returns relevant long-term memory + user profile summary.
        """
        long_term_context = self.long_term.retrieve(goal)

        profile = self.user_profile.get_profile()
        profile_summary = f"User profile: {profile}"

        return "\n".join(
            part for part in [long_term_context, profile_summary] if part
        )

    # -------------------------------------------------
    # Called EVERY STEP by controller
    # -------------------------------------------------

    def store_step(self, goal, action, success, result, observation):
        """
        Stores step info into short-term memory,
        and selectively into long-term memory.
        """

        # --- Short-term memory (always) ---
        step_summary = (
            f"Action: {action} | "
            f"Success: {success} | "
            f"Observation: {observation}"
        )
        self.short_term.add(step_summary)

        # --- Long-term memory (only meaningful events) ---
        if not success:
            self.long_term.add_memory(
                text=(
                    f"Failure while working on goal '{goal}'. "
                    f"Action: {action}. Observation: {observation}."
                ),
                metadata={"type": "failure"},
            )

        if success and action.get("type") == "STOP":
            self.long_term.add_memory(
                text=(
                    f"Completed goal '{goal}' successfully. "
                    f"Final observation: {observation}."
                ),
                metadata={"type": "success"},
            )

    # -------------------------------------------------
    # Called after task ends
    # -------------------------------------------------

    def reset_short_term(self):
        self.short_term.reset()
