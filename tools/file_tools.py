from tools.base_tool import BaseTool


class ReadFileTool(BaseTool):
    name = "READ_FILE"

    def run(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()


class WriteFileTool(BaseTool):
    name = "WRITE_FILE"

    def run(self, path: str, content: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Wrote file at {path}"
