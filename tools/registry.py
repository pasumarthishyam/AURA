class ToolRegistry:
    """
    Registry mapping tool names to tool instances.
    """

    def __init__(self):
        self._tools = {}

    def register(self, tool):
        if not tool.name:
            raise ValueError("Tool must have a name")
        self._tools[tool.name] = tool

    def get(self, tool_name: str):
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        return self._tools[tool_name]

    def list_tools(self):
        return list(self._tools.keys())
