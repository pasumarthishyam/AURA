from tools.base_tool import BaseTool


class ReadFileTool(BaseTool):
    name = "read_file"

    def run(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()


class WriteFileTool(BaseTool):
    name = "write_file"

    def run(self, path: str, content: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Wrote file at {path}"
