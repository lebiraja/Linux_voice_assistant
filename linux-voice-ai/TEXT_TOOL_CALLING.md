# Text-Based Tool Calling - Quick Reference

## How It Works

Instead of complex function calling, the LLM responds with a simple text marker:

```
TOOL: get_system_info(info_type="all")
```

We parse this, execute the tool, and send results back to LLM for formatting.

## Example Flow

**User:** "show me my system status"

**LLM Response:**
```
TOOL: get_system_info(info_type="all")
```

**We Parse:** 
- Tool: `get_system_info`
- Params: `{"info_type": "all"}`

**Execute Tool:**
```python
result = tool_executor.execute("get_system_info", {"info_type": "all"})
# Returns: CPU 25%, RAM 4GB/8GB, Disk 120GB free
```

**Send Back to LLM:**
```
Tool 'get_system_info' returned:
CPU: 25% usage, 4 cores
RAM: 4GB used, 4GB available (50%)
Disk: 120GB free, 200GB total

Provide answer to: show me my system status
```

**Final LLM Response:**
```
Your system is running well. CPU is at 25%, you have 4GB of RAM available, and 120GB of free disk space.
```

## Advantages

✅ **Simple** - No complex function schemas
✅ **Reliable** - Works with any LLM
✅ **Debuggable** - Easy to see what's happening
✅ **Flexible** - Easy to add new tools

## Tool Format

```
TOOL: tool_name(param1="value1", param2="value2")
```

Examples:
- `TOOL: get_system_info(info_type="cpu")`
- `TOOL: list_files(path=".", pattern="*.py")`
- `TOOL: search_web(query="Python tutorials")`
