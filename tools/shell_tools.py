import subprocess
from tools.base_tool import BaseTool


class ShellTool(BaseTool):
    name = "SHELL_EXECUTE"

    def run(self, command: str):
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        if process.returncode != 0:
            raise Exception(process.stderr.strip())

        return process.stdout.strip()
