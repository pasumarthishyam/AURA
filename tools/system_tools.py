import webbrowser
import subprocess
import sys
from tools.base_tool import BaseTool


class OpenBrowserTool(BaseTool):
    name = "open_browser"

    def run(self, url: str):
        webbrowser.open(url)
        return f"Opened browser at {url}"


class OpenAppTool(BaseTool):
    name = "open_app"

    def run(self, name: str):
        try:
            if sys.platform.startswith("win"):
                subprocess.Popen([name])
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", "-a", name])
            else:
                subprocess.Popen([name])
        except Exception:
            raise Exception(f"Application '{name}' not found")

        return f"Opened application {name}"
