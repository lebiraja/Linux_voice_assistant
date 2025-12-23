"""
System Prompts for LLM
Defines system prompts and templates for different interaction modes
"""


class SystemPrompts:
    """Collection of system prompts for the voice assistant"""
    
    ASSISTANT_SYSTEM_PROMPT = """You are JARVIS, an intelligent voice assistant for Linux systems.

Your capabilities:
- Control applications (open, close, launch programs)
- Query system information (CPU, RAM, disk usage)
- Execute file operations
- Search the web
- Answer questions and have conversations

Guidelines:
- Be concise and direct in your responses (you will be spoken aloud)
- When asked to perform an action, confirm what you're doing
- If you need to use a tool, call the appropriate function
- If something is unclear, ask for clarification
- Keep responses under 2-3 sentences when possible

Current context: You are running on a Linux desktop system."""

    COMMAND_UNDERSTANDING_PROMPT = """Analyze the user's command and determine the intent.

User command: {command}

Determine:
1. What action does the user want to perform?
2. What is the target (app name, file, query, etc.)?
3. Are there any parameters or modifiers?

Respond in a structured way that can be used to execute the command."""

    TOOL_SELECTION_PROMPT = """You have access to the following tools:
{tools}

User request: {request}

Which tool(s) should be used to fulfill this request? Explain your reasoning briefly."""

    CONTEXT_AWARE_PROMPT = """Previous conversation:
{context}

Current request: {request}

Consider the conversation history when responding. If the user refers to something mentioned earlier (like "it", "that", "the same"), use the context to understand what they mean."""

    ERROR_HANDLING_PROMPT = """An error occurred while processing the user's request.

Error: {error}
User request: {request}

Provide a helpful, conversational response explaining what went wrong and suggest what the user might try instead."""

    @staticmethod
    def get_system_prompt(include_tools: bool = False, tools: list = None) -> str:
        """
        Get the main system prompt, optionally including tool descriptions.
        
        Args:
            include_tools: Whether to include tool descriptions
            tools: List of tool schemas
            
        Returns:
            str: Formatted system prompt
        """
        prompt = SystemPrompts.ASSISTANT_SYSTEM_PROMPT
        
        if include_tools and tools:
            tool_descriptions = "\n".join([
                f"- {tool['name']}: {tool['description']}"
                for tool in tools
            ])
            prompt += f"\n\nAvailable tools:\n{tool_descriptions}"
        
        return prompt
    
    @staticmethod
    def format_command_prompt(command: str) -> str:
        """Format a command understanding prompt"""
        return SystemPrompts.COMMAND_UNDERSTANDING_PROMPT.format(command=command)
    
    @staticmethod
    def format_context_prompt(context: str, request: str) -> str:
        """Format a context-aware prompt"""
        return SystemPrompts.CONTEXT_AWARE_PROMPT.format(
            context=context,
            request=request
        )
    
    @staticmethod
    def format_error_prompt(error: str, request: str) -> str:
        """Format an error handling prompt"""
        return SystemPrompts.ERROR_HANDLING_PROMPT.format(
            error=error,
            request=request
        )
