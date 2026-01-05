"""
Test script to verify all tools are properly registered.
"""
import sys
sys.path.insert(0, '.')

from tools.executor import Executor

executor = Executor()

print("=== Registered Tools ===")
for tool_name in executor.registry.list_tools():
    print(f"  ✅ {tool_name}")

print("\n=== Testing SHELL_EXECUTE ===")
try:
    result = executor.execute({
        "type": "ACTION",
        "tool": "SHELL_EXECUTE",
        "params": {"command": "echo Hello from JARVIS"}
    })
    print(f"  Result: {result}")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n=== Testing OPEN_BROWSER ===")
try:
    result = executor.execute({
        "type": "ACTION",
        "tool": "OPEN_BROWSER",
        "params": {"url": "https://www.google.com"}
    })
    print(f"  Result: {result}")
except Exception as e:
    print(f"  ❌ Error: {e}")
