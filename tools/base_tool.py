class BaseTool:
    """
    Base class for all tools.
    """

    name = None  # must be overridden

    def run(self, **kwargs):
        raise NotImplementedError("Tool must implement run()")
