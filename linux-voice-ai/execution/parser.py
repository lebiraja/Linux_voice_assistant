"""
Robust Tool Call Parser.
Handles various LLM output formats and extracts tool calls reliably.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """Represents a parsed tool call"""
    name: str
    params: Dict[str, Any]
    raw: str  # Original matched text
    confidence: float = 1.0


class ToolCallParser:
    """
    Robust parser for extracting tool calls from LLM responses.

    Supports multiple formats:
    - TOOL: name(param="value")
    - [CALL: name(param="value")]
    - ```tool name(param="value")```
    - Function call style: name(param="value")
    """

    # Valid tool names (will be populated from registry)
    VALID_TOOLS = {
        # App control
        'open_app', 'close_app', 'run_script',
        # System
        'get_system_info', 'get_processes', 'execute_command',
        # Filesystem
        'list_files', 'read_file', 'search_files',
        # Web
        'search_web', 'fetch_url', 'open_website', 'web_search',
        # Script generation
        'generate_and_run_script',
        # Media control
        'control_media', 'get_now_playing',
        # Conversation
        'answer_question', 'explain_concept', 'have_conversation',
        # User context
        'set_user_preference', 'remember_user_info', 'set_work_context',
        # System Control
        'control_brightness', 'power_management', 'control_system_volume',
    }

    # Patterns to match tool calls (ordered by specificity)
    PATTERNS = [
        # Standard format: TOOL: name(params)
        r'TOOL:\s*(\w+)\s*\(([^)]*)\)',

        # Bracketed format: [CALL: name(params)]
        r'\[CALL:\s*(\w+)\s*\(([^)]*)\)\]',

        # Markdown code block: ```tool name(params)```
        r'```tool\s+(\w+)\s*\(([^)]*)\)```',

        # JSON-like: {"tool": "name", "params": {...}}
        # Handled separately

        # Bare function call: name(params) - only if name is valid
        r'\b(\w+)\s*\(([^)]*)\)',
    ]

    # Pattern to match thinking blocks
    THINKING_PATTERN = re.compile(r'<think>.*?</think>', re.DOTALL | re.IGNORECASE)

    # Pattern to match various thinking variations
    THINKING_VARIATIONS = [
        re.compile(r'<thinking>.*?</thinking>', re.DOTALL | re.IGNORECASE),
        re.compile(r'\[thinking\].*?\[/thinking\]', re.DOTALL | re.IGNORECASE),
        re.compile(r'<reasoning>.*?</reasoning>', re.DOTALL | re.IGNORECASE),
    ]

    def __init__(self, valid_tools: set = None):
        """
        Initialize parser.

        Args:
            valid_tools: Set of valid tool names. If None, uses default set.
        """
        self.valid_tools = valid_tools or self.VALID_TOOLS.copy()

    def update_valid_tools(self, tools: set):
        """Update the set of valid tool names"""
        self.valid_tools = tools

    def parse(self, response: str) -> List[ToolCall]:
        """
        Parse tool calls from LLM response.

        Args:
            response: Raw LLM response text

        Returns:
            List of ToolCall objects
        """
        if not response:
            return []

        # Clean the response
        cleaned = self._clean_response(response)

        tool_calls = []
        seen = set()  # Avoid duplicates

        # Try each pattern
        for i, pattern in enumerate(self.PATTERNS):
            for match in re.finditer(pattern, cleaned, re.IGNORECASE):
                tool_name = match.group(1)
                params_str = match.group(2)

                # Validate tool name
                if not self._is_valid_tool(tool_name):
                    # For bare function pattern, skip invalid names
                    if i == len(self.PATTERNS) - 1:  # Last pattern (bare function)
                        continue
                    logger.debug(f"Skipping invalid tool: {tool_name}")
                    continue

                # Parse parameters
                params = self._parse_params(params_str)

                # Create unique key to avoid duplicates
                key = f"{tool_name}:{sorted(params.items())}"
                if key in seen:
                    continue
                seen.add(key)

                # Calculate confidence based on pattern specificity
                confidence = 1.0 - (i * 0.1)  # Earlier patterns = higher confidence

                tool_calls.append(ToolCall(
                    name=tool_name,
                    params=params,
                    raw=match.group(0),
                    confidence=confidence
                ))

        # Try JSON format as fallback
        json_calls = self._parse_json_format(cleaned)
        for call in json_calls:
            key = f"{call.name}:{sorted(call.params.items())}"
            if key not in seen:
                seen.add(key)
                tool_calls.append(call)

        # Sort by confidence
        tool_calls.sort(key=lambda x: x.confidence, reverse=True)

        if tool_calls:
            logger.info(f"Parsed {len(tool_calls)} tool calls: {[t.name for t in tool_calls]}")
        else:
            logger.debug("No tool calls found in response")

        return tool_calls

    def parse_single(self, response: str) -> Optional[ToolCall]:
        """Parse and return only the first (best) tool call"""
        calls = self.parse(response)
        return calls[0] if calls else None

    def _clean_response(self, response: str) -> str:
        """Remove thinking blocks and clean up response"""
        cleaned = response

        # Remove <think>...</think> blocks
        cleaned = self.THINKING_PATTERN.sub('', cleaned)

        # Remove other thinking variations
        for pattern in self.THINKING_VARIATIONS:
            cleaned = pattern.sub('', cleaned)

        # Remove markdown code block markers (but keep content)
        cleaned = re.sub(r'```\w*\n?', '', cleaned)

        # Normalize whitespace
        cleaned = ' '.join(cleaned.split())

        return cleaned.strip()

    def _is_valid_tool(self, tool_name: str) -> bool:
        """Check if tool name is valid"""
        return tool_name.lower() in {t.lower() for t in self.valid_tools}

    def _parse_params(self, params_str: str) -> Dict[str, Any]:
        """
        Parse parameter string into dictionary.

        Handles:
        - key="value" (quoted strings)
        - key='value' (single quotes)
        - key=123 (numbers)
        - key=true/false (booleans)
        - key=value (unquoted strings)
        """
        params = {}

        if not params_str or not params_str.strip():
            return params

        # Match key=value patterns
        # Handle quoted strings first (they may contain commas)
        remaining = params_str

        # Double-quoted strings
        for match in re.finditer(r'(\w+)\s*=\s*"([^"]*)"', remaining):
            params[match.group(1)] = match.group(2)

        # Single-quoted strings
        for match in re.finditer(r"(\w+)\s*=\s*'([^']*)'", remaining):
            if match.group(1) not in params:
                params[match.group(1)] = match.group(2)

        # Unquoted values (numbers, booleans, simple strings)
        for match in re.finditer(r'(\w+)\s*=\s*([^,\s\)]+)', remaining):
            key = match.group(1)
            if key in params:
                continue  # Already parsed as quoted

            value = match.group(2).strip()
            params[key] = self._convert_value(value)

        return params

    def _convert_value(self, value: str) -> Any:
        """Convert string value to appropriate Python type"""
        # Strip quotes if present
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]

        # Boolean
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False

        # None/null
        if value.lower() in ('none', 'null'):
            return None

        # Integer
        if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
            return int(value)

        # Float
        try:
            if '.' in value:
                return float(value)
        except ValueError:
            pass

        # String (default)
        return value

    def _parse_json_format(self, response: str) -> List[ToolCall]:
        """Try to parse JSON-formatted tool calls"""
        import json

        calls = []

        # Look for JSON objects
        json_pattern = r'\{[^{}]*"tool"[^{}]*\}'

        for match in re.finditer(json_pattern, response):
            try:
                data = json.loads(match.group(0))
                tool_name = data.get('tool') or data.get('name') or data.get('function')
                params = data.get('params') or data.get('parameters') or data.get('args') or {}

                if tool_name and self._is_valid_tool(tool_name):
                    calls.append(ToolCall(
                        name=tool_name,
                        params=params,
                        raw=match.group(0),
                        confidence=0.8  # Slightly lower confidence for JSON format
                    ))
            except json.JSONDecodeError:
                continue

        return calls

    def has_tool_call(self, response: str) -> bool:
        """Quick check if response contains any tool call"""
        cleaned = self._clean_response(response)

        # Quick pattern checks
        if 'TOOL:' in cleaned or 'CALL:' in cleaned:
            return True

        # Check for known tool names followed by parentheses
        for tool in self.valid_tools:
            if re.search(rf'\b{tool}\s*\(', cleaned, re.IGNORECASE):
                return True

        return False

    def extract_direct_response(self, response: str) -> Optional[str]:
        """
        Extract any direct text response (not a tool call).
        Returns the text that should be spoken to the user.
        """
        cleaned = self._clean_response(response)

        # Remove all tool call patterns
        for pattern in self.PATTERNS:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        # Remove JSON tool calls
        cleaned = re.sub(r'\{[^{}]*"tool"[^{}]*\}', '', cleaned)

        # Clean up remaining text
        cleaned = ' '.join(cleaned.split())
        cleaned = cleaned.strip()

        # Filter out common non-response patterns
        ignore_patterns = [
            r'^okay[,.]?\s*$',
            r'^sure[,.]?\s*$',
            r'^alright[,.]?\s*$',
            r'^let me\b',
            r'^i will\b',
            r'^i\'ll\b',
        ]

        for pattern in ignore_patterns:
            if re.match(pattern, cleaned.lower()):
                return None

        return cleaned if cleaned else None


# Convenience function
def parse_tool_calls(response: str, valid_tools: set = None) -> List[ToolCall]:
    """Parse tool calls from response"""
    parser = ToolCallParser(valid_tools)
    return parser.parse(response)


def parse_single_tool_call(response: str, valid_tools: set = None) -> Optional[ToolCall]:
    """Parse single (best) tool call from response"""
    parser = ToolCallParser(valid_tools)
    return parser.parse_single(response)
