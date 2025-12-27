"""
Tool registry for managing available tools
"""

import logging
from typing import Dict, List, Optional
from .base import Tool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for managing available tools"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        logger.info("ToolRegistry initialized")
    
    def register(self, tool: Tool) -> None:
        """
        Register a tool.
        
        Args:
            tool: Tool instance to register
        """
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def unregister(self, tool_name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            tool_name: Name of tool to unregister
            
        Returns:
            bool: True if unregistered, False if not found
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")
            return True
        return False
    
    def get(self, tool_name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool instance or None if not found
        """
        return self.tools.get(tool_name)
    
    def get_all(self) -> List[Tool]:
        """Get all registered tools"""
        return list(self.tools.values())
    
    def get_all_schemas(self) -> List[Dict]:
        """
        Get all tool schemas for LLM.
        
        Returns:
            list: List of function schemas
        """
        return [tool.to_function_schema() for tool in self.tools.values()]
    
    def list_tools(self) -> List[str]:
        """Get list of all tool names"""
        return list(self.tools.keys())
    
    def __len__(self) -> int:
        """Get number of registered tools"""
        return len(self.tools)
    
    def __contains__(self, tool_name: str) -> bool:
        """Check if tool is registered"""
        return tool_name in self.tools
