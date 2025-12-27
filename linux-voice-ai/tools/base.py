"""
Tool base classes and interfaces
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ToolParameter:
    """Represents a tool parameter"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


class Tool(ABC):
    """Base class for all tools"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (used by LLM to call the tool)"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for LLM"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """Tool parameters"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            dict: Result with 'success' and 'data' or 'error'
        """
        pass
    
    def to_function_schema(self) -> Dict:
        """
        Convert to function calling schema for LLM.
        
        Returns:
            dict: OpenAI-compatible function schema
        """
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            if param.default is not None:
                properties[param.name]["default"] = param.default
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    def validate_parameters(self, **kwargs) -> tuple[bool, Optional[str]]:
        """
        Validate parameters before execution.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                return False, f"Missing required parameter: {param.name}"
        
        return True, None
