"""
Improved System Prompts for JARVIS AI assistant.
Optimized for reliable tool calling and natural conversation.
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ImprovedPrompts:
    """
    Improved prompt system with:
    - Compact, efficient prompts
    - Clear tool calling format
    - Few-shot examples
    - Dynamic capability awareness
    """

    # Core system prompt - personality and basics
    SYSTEM_PROMPT = """You are JARVIS, a helpful voice assistant for Linux systems.

RULES:
1. For actions, respond with: TOOL: name(param="value")
2. For conversation, respond naturally in 1-2 sentences
3. Be concise - responses are spoken aloud
4. If unsure, ask for clarification

PERSONALITY:
- Helpful and efficient
- Direct and clear
- Friendly but professional"""

    # Compact tool reference
    TOOL_REFERENCE = """
AVAILABLE TOOLS:

[App Control]
• open_app(app_name) - Open app: "open firefox" → TOOL: open_app(app_name="firefox")
• close_app(app_name) - Close app: "close chrome" → TOOL: close_app(app_name="chrome")

[System Info]
• get_system_info(info_type) - CPU/RAM/disk: "cpu usage" → TOOL: get_system_info(info_type="cpu")
  info_type: "cpu", "memory", "disk", "all"

[System Control]
• control_brightness(action, value) - Screen: "brightness 80" → TOOL: control_brightness(action="set", value=80)
• control_system_volume(action, value) - Volume: "volume 50" → TOOL: control_system_volume(action="set", value=50)
• power_management(action) - Power: "lock screen" → TOOL: power_management(action="lock")
  action: "get", "set", "increase", "decrease", "mute", "unmute"

[Media]
• control_media(action) - Playback: "pause music" → TOOL: control_media(action="pause")
  action: "play", "pause", "stop", "next", "previous"
• get_now_playing() - Current track: "what's playing" → TOOL: get_now_playing()

[Files]
• list_files(path, pattern) - List: "python files" → TOOL: list_files(pattern="*.py")
• read_file(file_path) - Read: "read config" → TOOL: read_file(file_path="config.yaml")

[Web]
• search_web(query) - Search: "search docker" → TOOL: search_web(query="docker")
• open_website(website) - Open site: "open github" → TOOL: open_website(website="github")

[Conversation]
• answer_question(question) - Q&A: "what is python" → TOOL: answer_question(question="What is Python?")
• have_conversation(message) - Chat: "hello" → TOOL: have_conversation(message="hello")

[Automation]
• generate_and_run_script(task_description) - AI script: "backup docs" → TOOL: generate_and_run_script(task_description="backup documents")
• run_script(script) - Command: "git status" → TOOL: run_script(script="git status")

RESPONSE FORMAT:
- Actions: TOOL: tool_name(param="value", param2=123)
- Greetings: Respond naturally (Hello! How can I help?)
- Unknown: Ask for clarification

CRITICAL: Output ONLY the TOOL call for actions. No explanations."""

    # Few-shot examples for better accuracy
    FEW_SHOT_EXAMPLES = """
EXAMPLES:

User: "open firefox"
TOOL: open_app(app_name="firefox")

User: "what's my CPU usage"
TOOL: get_system_info(info_type="cpu")

User: "set brightness to 80 percent"
TOOL: control_brightness(action="set", value=80)

User: "pause the music"
TOOL: control_media(action="pause")

User: "what is Docker"
TOOL: answer_question(question="What is Docker?")

User: "hello"
Hello! I'm JARVIS. How can I help you today?

User: "open youtube"
TOOL: open_website(website="youtube")

User: "create a script to list all jpg files"
TOOL: generate_and_run_script(task_description="list all jpg files")
"""

    # Conversation-specific prompt
    CONVERSATION_PROMPT = """You are JARVIS, answering a question or having a conversation.

GUIDELINES:
- Be informative but concise (2-3 sentences max)
- Responses will be spoken aloud
- Be friendly and helpful
- Use clear, simple language

If this is a greeting, respond warmly.
If this is a question, provide a helpful answer.
If asked about yourself, explain you're a Linux voice assistant."""

    # Tool result summary prompt
    RESULT_SUMMARY_PROMPT = """Based on the tool results below, provide a brief spoken confirmation.

GUIDELINES:
- Keep it to 1-2 sentences
- Be specific about what was done
- Use natural language
- Don't repeat technical details verbatim

USER REQUEST: {request}

TOOL RESULTS:
{results}

Respond with a brief, natural confirmation of what was accomplished:"""

    @classmethod
    def get_full_prompt(cls) -> str:
        """Get complete system prompt for tool calling"""
        return f"{cls.SYSTEM_PROMPT}\n\n{cls.TOOL_REFERENCE}\n\n{cls.FEW_SHOT_EXAMPLES}"

    @classmethod
    def get_compact_prompt(cls) -> str:
        """Get minimal prompt for simple commands"""
        return f"{cls.SYSTEM_PROMPT}\n\n{cls.TOOL_REFERENCE}"

    @classmethod
    def get_conversation_prompt(cls) -> str:
        """Get prompt for conversational responses"""
        return cls.CONVERSATION_PROMPT

    @classmethod
    def format_result_prompt(cls, request: str, results: str) -> str:
        """Format prompt for summarizing tool results"""
        return cls.RESULT_SUMMARY_PROMPT.format(
            request=request,
            results=results
        )

    @classmethod
    def get_category_prompt(cls, category: str) -> str:
        """Get focused prompt for specific category"""
        category_prompts = {
            "app_control": """Tools for app control:
• open_app(app_name) - Open: TOOL: open_app(app_name="firefox")
• close_app(app_name) - Close: TOOL: close_app(app_name="chrome")""",

            "system_info": """Tools for system info:
• get_system_info(info_type) - TOOL: get_system_info(info_type="cpu")
  Types: cpu, memory, disk, all""",

            "system_control": """Tools for system control:
• control_brightness(action, value) - TOOL: control_brightness(action="set", value=80)
• control_system_volume(action, value) - TOOL: control_system_volume(action="set", value=50)
• power_management(action) - TOOL: power_management(action="lock")""",

            "media": """Tools for media:
• control_media(action) - TOOL: control_media(action="play")
  Actions: play, pause, stop, next, previous
• get_now_playing() - TOOL: get_now_playing()""",

            "files": """Tools for files:
• list_files(path, pattern) - TOOL: list_files(pattern="*.py")
• read_file(file_path) - TOOL: read_file(file_path="config.yaml")
• search_files(path, pattern) - TOOL: search_files(pattern="test")""",

            "web": """Tools for web:
• search_web(query) - TOOL: search_web(query="python tutorial")
• open_website(website) - TOOL: open_website(website="github")""",

            "conversation": """For questions/chat:
• answer_question(question) - TOOL: answer_question(question="What is X?")
• have_conversation(message) - TOOL: have_conversation(message="hello")
Or respond naturally for greetings.""",

            "automation": """Tools for automation:
• generate_and_run_script(task_description) - TOOL: generate_and_run_script(task_description="task")
• run_script(script) - TOOL: run_script(script="ls -la")"""
        }

        return category_prompts.get(category, cls.TOOL_REFERENCE)


class DynamicPromptBuilder:
    """
    Builds optimized prompts based on context and detected intent category.
    """

    def __init__(self, manifest=None):
        """
        Initialize with capability manifest.

        Args:
            manifest: CapabilityManifest instance for dynamic tool discovery
        """
        self.manifest = manifest
        self.base_prompt = ImprovedPrompts.SYSTEM_PROMPT

    def build_prompt(self, user_input: str, context: str = None) -> str:
        """
        Build optimized prompt for user input.

        Args:
            user_input: The user's command/question
            context: Optional conversation context

        Returns:
            Complete system prompt optimized for this input
        """
        # Detect category if manifest available
        if self.manifest:
            category = self.manifest.detect_category(user_input)
            if category:
                return self._build_focused_prompt(category, context)

        # Default to full prompt
        return self._build_full_prompt(context)

    def _build_focused_prompt(self, category: str, context: str = None) -> str:
        """Build category-focused prompt"""
        parts = [
            self.base_prompt,
            "",
            "RESPONSE FORMAT: TOOL: name(param=\"value\")",
            "",
            ImprovedPrompts.get_category_prompt(category)
        ]

        if context:
            parts.insert(0, f"CONTEXT:\n{context}\n")

        return "\n".join(parts)

    def _build_full_prompt(self, context: str = None) -> str:
        """Build complete prompt"""
        prompt = ImprovedPrompts.get_full_prompt()

        if context:
            prompt = f"CONTEXT:\n{context}\n\n{prompt}"

        return prompt

    def build_result_prompt(
        self,
        user_request: str,
        tool_results: List[Dict],
        is_conversation: bool = False
    ) -> str:
        """
        Build prompt for summarizing tool results.

        Args:
            user_request: Original user request
            tool_results: List of tool execution results
            is_conversation: Whether this was a conversational query
        """
        # Format results
        results_text = []
        for result in tool_results:
            tool_name = result.get('tool', 'unknown')
            if result.get('success'):
                data = result.get('result', {})
                results_text.append(f"{tool_name}: {self._format_result(data)}")
            else:
                error = result.get('error', 'Unknown error')
                results_text.append(f"{tool_name}: Error - {error}")

        results_str = "\n".join(results_text)

        if is_conversation:
            return f"""{ImprovedPrompts.CONVERSATION_PROMPT}

User asked: "{user_request}"

Information gathered:
{results_str}

Provide a helpful, natural response:"""
        else:
            return ImprovedPrompts.format_result_prompt(user_request, results_str)

    def _format_result(self, data: any, max_length: int = 200) -> str:
        """Format result data for prompt"""
        if isinstance(data, dict):
            # Extract key information
            parts = []
            for key, value in list(data.items())[:5]:  # Limit keys
                if isinstance(value, (dict, list)):
                    parts.append(f"{key}: [complex data]")
                else:
                    parts.append(f"{key}: {value}")
            return ", ".join(parts)
        elif isinstance(data, list):
            return f"[{len(data)} items]"
        else:
            result = str(data)
            if len(result) > max_length:
                return result[:max_length] + "..."
            return result


# Backwards compatibility with old prompt class
class SystemPrompts:
    """Legacy compatibility wrapper"""

    ASSISTANT_SYSTEM_PROMPT = ImprovedPrompts.SYSTEM_PROMPT
    TOOL_CALLING_PROMPT = ImprovedPrompts.TOOL_REFERENCE

    @staticmethod
    def get_system_prompt(include_tools: bool = False, tools: list = None) -> str:
        if include_tools:
            return ImprovedPrompts.get_full_prompt()
        return ImprovedPrompts.SYSTEM_PROMPT
