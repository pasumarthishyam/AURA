class ShortTermMemory:
    """
    Ephemeral working memory for a single agent session.
    Cleared after task completion.
    """

    def __init__(self, max_items: int = 5):
        self.max_items = max_items
        self.buffer = []

    def add(self, text: str):
        if text:
            self.buffer.append(text)
            if len(self.buffer) > self.max_items:
                self.buffer.pop(0)

    def get_context(self) -> str:
        return "\n".join(self.buffer)

    def reset(self):
        self.buffer = []
