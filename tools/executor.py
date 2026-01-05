from tools.registry import ToolRegistry
from tools.system_tools import OpenBrowserTool, OpenAppTool
from tools.shell_tools import ShellTool
from tools.file_tools import ReadFileTool, WriteFileTool, WriteAndOpenTool
# Search Tools - DuckDuckGo primary with Google fallback
from tools.google_tools import WebSearchTool, GoogleSearchTool
import logging

logger = logging.getLogger("AURA.Executor")

# Tools that require internet connection
ONLINE_ONLY_TOOLS = {"SEARCH_WEB", "SEARCH_GOOGLE", "OPEN_BROWSER"}


class Executor:
    """
    Executes actions by dispatching to tools.
    Handles offline mode gracefully for online-only tools.
    """

    def __init__(self):
        self.registry = ToolRegistry()

        # Register tools
        self.registry.register(OpenBrowserTool())
        self.registry.register(OpenAppTool())
        self.registry.register(ShellTool())
        self.registry.register(ReadFileTool())
        self.registry.register(WriteFileTool())
        self.registry.register(WriteAndOpenTool())  # New compound tool
        # Search tools - SEARCH_WEB is the new primary
        self.registry.register(WebSearchTool())
        self.registry.register(GoogleSearchTool())  # Legacy compatibility

    def execute(self, action: dict):
        """
        Execute a single action.
        Handles offline mode gracefully for web-dependent tools.
        """

        if action.get("type") != "ACTION":
            raise ValueError("Executor received non-ACTION type")

        tool_name = action.get("tool")
        params = action.get("params", {})

        # Check offline mode for online-only tools
        from core.offline_state import OfflineState
        if OfflineState.is_offline() and tool_name in ONLINE_ONLY_TOOLS:
            return self._get_offline_message(tool_name, params)

        tool = self.registry.get(tool_name)
        return tool.run(**params)
    
    def _get_offline_message(self, tool_name: str, params: dict) -> str:
        """
        Return a friendly message when an online-only tool is called offline.
        """
        query = params.get("query", params.get("url", ""))
        
        if tool_name in {"SEARCH_WEB", "SEARCH_GOOGLE"}:
            return (
                f"📴 Currently in offline mode - web search is unavailable.\n"
                f"Your search: \"{query}\"\n\n"
                f"💡 I'll answer using my built-in knowledge instead.\n"
                f"Once you're connected to the internet, web search will work again."
            )
        elif tool_name == "OPEN_BROWSER":
            return (
                f"📴 Currently in offline mode - cannot open web pages.\n"
                f"URL requested: {query}\n\n"
                f"💡 Once you're connected to the internet, I can open this for you."
            )
        else:
            return (
                f"📴 '{tool_name}' requires internet connection.\n"
                f"This feature will work once you're connected to the internet."
            )

