import os
from tools.base_tool import BaseTool


class ReadFileTool(BaseTool):
    name = "READ_FILE"

    def run(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()


class WriteFileTool(BaseTool):
    name = "WRITE_FILE"

    def run(self, path: str, content: str):
        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Wrote file at {path}"


class WriteAndOpenTool(BaseTool):
    """
    Compound tool that writes content to a file AND opens it in the default application.
    Perfect for "write in notepad" type requests.
    """
    name = "WRITE_AND_OPEN"

    def run(self, path: str, content: str):
        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        
        # Write the file
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Open the file in default application (Notepad for .txt on Windows)
        try:
            os.startfile(path)
            return f"Wrote and opened file at {path}"
        except Exception as e:
            # Fallback: file was written but couldn't open
            return f"Wrote file at {path} (could not auto-open: {e})"

