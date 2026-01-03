from tools.registry import ToolRegistry
from tools.system_tools import OpenBrowserTool, OpenAppTool
from tools.shell_tools import ShellTool
from tools.file_tools import ReadFileTool, WriteFileTool
# Search Tools - DuckDuckGo primary with Google fallback
from tools.google_tools import WebSearchTool, GoogleSearchTool


class Executor:
    """
    Executes actions by dispatching to tools.
    """

    def __init__(self):
        self.registry = ToolRegistry()

        # Register tools
        self.registry.register(OpenBrowserTool())
        self.registry.register(OpenAppTool())
        self.registry.register(ShellTool())
        self.registry.register(ReadFileTool())
        self.registry.register(WriteFileTool())
        # Search tools - SEARCH_WEB is the new primary
        self.registry.register(WebSearchTool())
        self.registry.register(GoogleSearchTool())  # Legacy compatibility

    def execute(self, action: dict):
        """
        Execute a single action.
        """

        if action.get("type") != "ACTION":
            raise ValueError("Executor received non-ACTION type")

        tool_name = action.get("tool")
        params = action.get("params", {})

        tool = self.registry.get(tool_name)

        return tool.run(**params)
