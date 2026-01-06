"""
Built-in tools
"""

from .filesystem import ListFilesTool, ReadFileTool, SearchFilesTool
from .system import GetSystemInfoTool, GetProcessesTool, ExecuteCommandTool
from .web import SearchWebTool, FetchURLTool
from .apps import OpenAppTool, RunScriptTool, CloseAppTool
from .script_generator import GenerateAndRunScriptTool, ExecuteCommandTool as ExecuteShellCommandTool
from .media_control import MediaControlTool, GetNowPlayingTool
from .conversation import AnswerQuestionTool, ExplainConceptTool, HaveConversationTool
from .user_context_tools import SetUserPreferenceTool, RememberUserInfoTool, SetWorkContextTool
from .brightness_control import BrightnessControlTool
from .power_management import PowerManagementTool
from .system_volume import SystemVolumeTool
from .web_navigation import OpenWebsiteTool, WebSearchTool

__all__ = [
    'ListFilesTool',
    'ReadFileTool',
    'SearchFilesTool',
    'GetSystemInfoTool',
    'GetProcessesTool',
    'ExecuteCommandTool',
    'SearchWebTool',
    'FetchURLTool',
    'OpenAppTool',
    'RunScriptTool',
    'CloseAppTool',
    'GenerateAndRunScriptTool',
    'ExecuteShellCommandTool',
    'MediaControlTool',
    'GetNowPlayingTool',
    'AnswerQuestionTool',
    'ExplainConceptTool',
    'HaveConversationTool',
    'SetUserPreferenceTool',
    'RememberUserInfoTool',
    'SetWorkContextTool',
    
    # System Control (New)
    'BrightnessControlTool',
    'PowerManagementTool',
    'SystemVolumeTool',
    
    # Web Navigation (New)
    'OpenWebsiteTool',
    'WebSearchTool',
]
