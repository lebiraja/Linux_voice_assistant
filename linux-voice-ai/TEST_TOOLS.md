# Quick Test - Tool Calling

Run this to test if tools work:

```bash
cd /home/lebi/projects/VFL/linux-voice-ai
source venv/bin/activate
python3 << 'EOF'
from tools.builtin.system import GetSystemInfoTool

# Test the tool directly
tool = GetSystemInfoTool()
result = tool.execute(info_type="all")

print("Tool Result:")
print(result)
EOF
```

This will verify the tools themselves work, independent of the LLM.

If this works, the issue is with how Ollama/functiongemma handles tool calling.

**Workaround:** Since functiongemma's tool calling might not work as expected with Ollama's API, we can:
1. Have LLM respond with which tool to use in text
2. Parse the response to extract tool name and params
3. Execute the tool
4. Send results back to LLM for final answer

This is a more reliable approach for now.
