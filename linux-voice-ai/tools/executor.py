"""
Tool executor for executing tool calls from LLM
"""

import logging
from typing import Dict, Any, List
from .base import Tool
from .registry import ToolRegistry

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes tool calls from LLM responses"""
    
    def __init__(self, registry: ToolRegistry):
        """
        Initialize tool executor.
        
        Args:
            registry: ToolRegistry instance
        """
        self.registry = registry
        logger.info("ToolExecutor initialized")
    
    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single tool call.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            
        Returns:
            dict: Execution result
        """
        logger.info(f"Executing tool: {tool_name} with params: {parameters}")
        
        # Get tool from registry
        tool = self.registry.get(tool_name)
        if not tool:
            error_msg = f"Tool not found: {tool_name}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "tool": tool_name
            }
        
        # Validate parameters
        is_valid, error_msg = tool.validate_parameters(**parameters)
        if not is_valid:
            logger.error(f"Parameter validation failed: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "tool": tool_name
            }
        
        # Execute tool
        try:
            result = tool.execute(**parameters)
            logger.info(f"Tool {tool_name} executed successfully")
            return {
                "success": True,
                "tool": tool_name,
                "result": result
            }
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg,
                "tool": tool_name
            }
    
    def execute_multiple(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls in sequence.
        
        Args:
            tool_calls: List of tool calls, each with 'name' and 'parameters'
            
        Returns:
            list: List of execution results
        """
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get('name')
            parameters = tool_call.get('parameters', {})
            
            result = self.execute(tool_name, parameters)
            results.append(result)
            
            # Stop on first failure if configured
            if not result.get('success'):
                logger.warning(f"Tool call failed, stopping execution chain")
                break
        
        return results
    
    def format_result_for_llm(self, result: Dict[str, Any]) -> str:
        """
        Format tool execution result for LLM.
        
        Args:
            result: Tool execution result
            
        Returns:
            str: Formatted result string
        """
        if result.get('success'):
            tool_result = result.get('result', {})
            return self._format_value(tool_result)
        else:
            return f"Error: {result.get('error', 'Unknown error')}"
    
    def _format_value(self, value: Any, indent: int = 0) -> str:
        """
        Recursively format a value for LLM consumption.
        
        Args:
            value: Value to format
            indent: Current indentation level
            
        Returns:
            str: Formatted string
        """
        prefix = "  " * indent
        
        if isinstance(value, dict):
            lines = []
            for k, v in value.items():
                # Skip 'success' key as it's redundant
                if k == 'success':
                    continue
                # Format nested dicts
                if isinstance(v, dict):
                    lines.append(f"{prefix}{k}:")
                    lines.append(self._format_value(v, indent + 1))
                elif isinstance(v, list):
                    lines.append(f"{prefix}{k}: {len(v)} items")
                    for i, item in enumerate(v[:5]):  # Limit to 5 items
                        if isinstance(item, dict):
                            lines.append(f"{prefix}  - {self._format_value(item, 0)}")
                        else:
                            lines.append(f"{prefix}  - {item}")
                    if len(v) > 5:
                        lines.append(f"{prefix}  ... and {len(v) - 5} more")
                else:
                    # Format key nicely
                    key_display = k.replace('_', ' ').title()
                    lines.append(f"{prefix}{key_display}: {v}")
            return "\n".join(lines)
        elif isinstance(value, list):
            return f"{len(value)} items"
        else:
            return str(value)
