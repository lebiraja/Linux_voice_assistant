"""
User context management tools
Allow JARVIS to learn and remember user information
"""

import logging
from typing import Dict, Any, List
from ..base import Tool, ToolParameter

logger = logging.getLogger(__name__)


class SetUserPreferenceTool(Tool):
    """Set user preference"""
    
    @property
    def name(self) -> str:
        return "set_user_preference"
    
    @property
    def description(self) -> str:
        return (
            "Remember a user preference or setting. Use when user explicitly states preferences "
            "like 'I prefer concise responses', 'Use Firefox as my browser', 'I like Python', etc."
        )
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="category",
                type="string",
                description="Preference category: response, app, programming, work, etc.",
                required=True
            ),
            ToolParameter(
                name="preference",
                type="string",
                description="The preference key",
                required=True
            ),
            ToolParameter(
                name="value",
                type="string",
                description="The preference value",
                required=True
            )
        ]
    
    def execute(
        self,
        category: str,
        preference: str,
        value: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Set user preference"""
        try:
            # Get user context from kwargs (injected by assistant)
            user_context = kwargs.get('_user_context')
            
            if not user_context:
                return {
                    "success": False,
                    "error": "User context not available"
                }
            
            user_context.set_preference(category, preference, value)
            
            return {
                "success": True,
                "message": f"I'll remember that you prefer {value} for {preference}",
                "category": category,
                "preference": preference,
                "value": value
            }
            
        except Exception as e:
            logger.error(f"Error setting preference: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class RememberUserInfoTool(Tool):
    """Remember important information about the user"""
    
    @property
    def name(self) -> str:
        return "remember_user_info"
    
    @property
    def description(self) -> str:
        return (
            "Remember important information about the user such as name, location, occupation, "
            "interests, or other personal details they share."
        )
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="info_type",
                type="string",
                description="Type of information: name, location, occupation, timezone, etc.",
                required=True
            ),
            ToolParameter(
                name="value",
                type="string",
                description="The information value",
                required=True
            )
        ]
    
    def execute(
        self,
        info_type: str,
        value: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Remember user information"""
        try:
            user_context = kwargs.get('_user_context')
            
            if not user_context:
                return {
                    "success": False,
                    "error": "User context not available"
                }
            
            user_context.set_user_info(info_type, value)
            
            return {
                "success": True,
                "message": f"Got it, I'll remember your {info_type}",
                "info_type": info_type,
                "value": value
            }
            
        except Exception as e:
            logger.error(f"Error remembering user info: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class SetWorkContextTool(Tool):
    """Set current work context"""
    
    @property
    def name(self) -> str:
        return "set_work_context"
    
    @property
    def description(self) -> str:
        return (
            "Remember the user's current work context such as current project, working directory, "
            "programming language, or tasks they're working on."
        )
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="context_type",
                type="string",
                description="Context type: current_project, project_directory, primary_language, task, etc.",
                required=True
            ),
            ToolParameter(
                name="value",
                type="string",
                description="The context value",
                required=True
            )
        ]
    
    def execute(
        self,
        context_type: str,
        value: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Set work context"""
        try:
            user_context = kwargs.get('_user_context')
            
            if not user_context:
                return {
                    "success": False,
                    "error": "User context not available"
                }
            
            user_context.set_work_context(context_type, value)
            
            return {
                "success": True,
                "message": f"Noted, I'll remember that context",
                "context_type": context_type,
                "value": value
            }
            
        except Exception as e:
            logger.error(f"Error setting work context: {e}")
            return {
                "success": False,
                "error": str(e)
            }
