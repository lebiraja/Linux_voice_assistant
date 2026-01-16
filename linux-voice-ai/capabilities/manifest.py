"""
Capability Manifest - Dynamic capability discovery and LLM teaching system.
This module teaches the LLM everything JARVIS can do in a compact, effective way.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .platform import PlatformDetector, PlatformAdapter, get_platform
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Capability:
    """Represents a single capability"""
    name: str
    category: str
    description: str
    tool_name: str
    triggers: List[str]
    example_input: str
    example_output: str
    available: bool = True
    requires: List[str] = None


class CapabilityManifest:
    """
    Dynamic manifest of all JARVIS capabilities.

    This class:
    1. Discovers what's available on this platform
    2. Organizes capabilities by category
    3. Generates compact LLM prompts
    4. Provides semantic matching for user input
    """

    # Category definitions with keywords for matching
    CATEGORIES = {
        "app_control": {
            "name": "Application Control",
            "keywords": ["open", "launch", "start", "close", "quit", "exit", "kill"],
            "description": "Launch and close applications"
        },
        "system_info": {
            "name": "System Information",
            "keywords": ["cpu", "ram", "memory", "disk", "storage", "usage", "processes"],
            "description": "Query system metrics and resources"
        },
        "system_control": {
            "name": "System Control",
            "keywords": ["volume", "brightness", "power", "shutdown", "restart", "lock", "sleep"],
            "description": "Control system settings and power"
        },
        "media": {
            "name": "Media Control",
            "keywords": ["play", "pause", "stop", "next", "previous", "song", "music", "spotify"],
            "description": "Control media playback"
        },
        "files": {
            "name": "File Operations",
            "keywords": ["file", "folder", "directory", "list", "read", "search", "find"],
            "description": "Work with files and directories"
        },
        "web": {
            "name": "Web Operations",
            "keywords": ["search", "google", "website", "browse", "url", "internet"],
            "description": "Web search and browsing"
        },
        "conversation": {
            "name": "Conversation",
            "keywords": ["what", "how", "why", "explain", "tell me", "hello", "hi", "thanks"],
            "description": "Questions, explanations, and chat"
        },
        "automation": {
            "name": "Automation",
            "keywords": ["script", "automate", "generate", "create", "command", "execute"],
            "description": "Generate and run scripts"
        }
    }

    def __init__(self):
        self.platform = PlatformDetector.detect()
        self.adapter = PlatformAdapter()
        self.capabilities: Dict[str, List[Capability]] = {cat: [] for cat in self.CATEGORIES}
        self._build_manifest()

    def _build_manifest(self):
        """Build the capability manifest based on platform"""

        # App Control
        self._add_capability("app_control", Capability(
            name="Open Application",
            category="app_control",
            description="Launch any application",
            tool_name="open_app",
            triggers=["open", "launch", "start"],
            example_input="open firefox",
            example_output='TOOL: open_app(app_name="firefox")'
        ))

        self._add_capability("app_control", Capability(
            name="Close Application",
            category="app_control",
            description="Close a running application",
            tool_name="close_app",
            triggers=["close", "quit", "kill"],
            example_input="close chrome",
            example_output='TOOL: close_app(app_name="chrome")'
        ))

        # System Info
        self._add_capability("system_info", Capability(
            name="System Info",
            category="system_info",
            description="Get CPU, RAM, or disk usage",
            tool_name="get_system_info",
            triggers=["cpu", "ram", "memory", "disk"],
            example_input="what's my CPU usage",
            example_output='TOOL: get_system_info(info_type="cpu")'
        ))

        self._add_capability("system_info", Capability(
            name="List Processes",
            category="system_info",
            description="Show running processes",
            tool_name="get_processes",
            triggers=["processes", "running", "tasks"],
            example_input="show running processes",
            example_output='TOOL: get_processes()'
        ))

        # System Control
        self._add_capability("system_control", Capability(
            name="Screen Brightness",
            category="system_control",
            description="Control screen brightness (0-100)",
            tool_name="control_brightness",
            triggers=["brightness", "screen", "dim", "bright"],
            example_input="set brightness to 80",
            example_output='TOOL: control_brightness(action="set", value=80)',
            available=self.adapter.get_brightness_interface() is not None
        ))

        self._add_capability("system_control", Capability(
            name="System Volume",
            category="system_control",
            description="Control system volume (0-100)",
            tool_name="control_system_volume",
            triggers=["volume", "sound", "mute", "loud", "quiet"],
            example_input="set volume to 50",
            example_output='TOOL: control_system_volume(action="set", value=50)',
            available=self.platform.has_amixer
        ))

        self._add_capability("system_control", Capability(
            name="Power Management",
            category="system_control",
            description="Shutdown, restart, suspend, or lock",
            tool_name="power_management",
            triggers=["shutdown", "restart", "sleep", "lock", "suspend"],
            example_input="lock the screen",
            example_output='TOOL: power_management(action="lock")',
            available=self.platform.has_systemd
        ))

        # Media Control
        self._add_capability("media", Capability(
            name="Media Playback",
            category="media",
            description="Play, pause, skip tracks",
            tool_name="control_media",
            triggers=["play", "pause", "stop", "next", "previous", "skip"],
            example_input="pause the music",
            example_output='TOOL: control_media(action="pause")',
            available=self.platform.has_playerctl,
            requires=["playerctl"]
        ))

        self._add_capability("media", Capability(
            name="Now Playing",
            category="media",
            description="Get current track information",
            tool_name="get_now_playing",
            triggers=["what's playing", "current song", "now playing"],
            example_input="what's playing",
            example_output='TOOL: get_now_playing()',
            available=self.platform.has_playerctl,
            requires=["playerctl"]
        ))

        # Files
        self._add_capability("files", Capability(
            name="List Files",
            category="files",
            description="List files in a directory",
            tool_name="list_files",
            triggers=["list", "show files", "directory", "ls"],
            example_input="list python files",
            example_output='TOOL: list_files(pattern="*.py")'
        ))

        self._add_capability("files", Capability(
            name="Read File",
            category="files",
            description="Read contents of a file",
            tool_name="read_file",
            triggers=["read", "show", "cat", "contents"],
            example_input="read config.yaml",
            example_output='TOOL: read_file(file_path="config.yaml")'
        ))

        self._add_capability("files", Capability(
            name="Search Files",
            category="files",
            description="Find files by name pattern",
            tool_name="search_files",
            triggers=["find", "search", "locate"],
            example_input="find all test files",
            example_output='TOOL: search_files(pattern="*test*")'
        ))

        # Web
        self._add_capability("web", Capability(
            name="Web Search",
            category="web",
            description="Search the internet",
            tool_name="search_web",
            triggers=["search", "google", "look up", "find online"],
            example_input="search for python tutorials",
            example_output='TOOL: search_web(query="python tutorials")'
        ))

        self._add_capability("web", Capability(
            name="Open Website",
            category="web",
            description="Open a website by name",
            tool_name="open_website",
            triggers=["open", "go to", "visit", "browse"],
            example_input="open youtube",
            example_output='TOOL: open_website(website="youtube")'
        ))

        # Conversation
        self._add_capability("conversation", Capability(
            name="Answer Question",
            category="conversation",
            description="Answer general questions",
            tool_name="answer_question",
            triggers=["what is", "what are", "how does", "explain", "tell me"],
            example_input="what is Docker",
            example_output='TOOL: answer_question(question="What is Docker?")'
        ))

        self._add_capability("conversation", Capability(
            name="Explain Concept",
            category="conversation",
            description="Explain technical concepts",
            tool_name="explain_concept",
            triggers=["explain", "how works", "what does"],
            example_input="explain how git works",
            example_output='TOOL: explain_concept(concept="git")'
        ))

        self._add_capability("conversation", Capability(
            name="Chat",
            category="conversation",
            description="Casual conversation",
            tool_name="have_conversation",
            triggers=["hello", "hi", "hey", "thanks", "how are you"],
            example_input="hello",
            example_output='TOOL: have_conversation(message="hello")'
        ))

        # Automation
        self._add_capability("automation", Capability(
            name="Generate Script",
            category="automation",
            description="AI generates and runs custom scripts",
            tool_name="generate_and_run_script",
            triggers=["create script", "write script", "automate", "generate code"],
            example_input="create a script to backup my documents",
            example_output='TOOL: generate_and_run_script(task_description="backup my documents")'
        ))

        self._add_capability("automation", Capability(
            name="Run Command",
            category="automation",
            description="Execute shell commands",
            tool_name="run_script",
            triggers=["run", "execute", "command"],
            example_input="run git status",
            example_output='TOOL: run_script(script="git status")'
        ))

        logger.info(f"Built manifest with {self.count_capabilities()} capabilities")

    def _add_capability(self, category: str, capability: Capability):
        """Add a capability to the manifest"""
        self.capabilities[category].append(capability)

    def count_capabilities(self) -> int:
        """Count total capabilities"""
        return sum(len(caps) for caps in self.capabilities.values())

    def count_available(self) -> int:
        """Count available capabilities on this platform"""
        return sum(
            1 for caps in self.capabilities.values()
            for cap in caps if cap.available
        )

    def get_available(self) -> Dict[str, List[Capability]]:
        """Get only available capabilities"""
        return {
            cat: [c for c in caps if c.available]
            for cat, caps in self.capabilities.items()
        }

    def detect_category(self, text: str) -> Optional[str]:
        """
        Detect which category a user input belongs to.
        Returns the most likely category based on keyword matching.
        """
        text_lower = text.lower()
        scores = {}

        for cat, info in self.CATEGORIES.items():
            score = 0
            for keyword in info["keywords"]:
                if keyword in text_lower:
                    score += 1
            if score > 0:
                scores[cat] = score

        if scores:
            return max(scores, key=scores.get)
        return None

    def get_relevant_tools(self, text: str) -> List[Capability]:
        """
        Get tools relevant to the user input.
        Uses category detection to reduce context.
        """
        category = self.detect_category(text)

        if category:
            # Return tools from matched category
            return [c for c in self.capabilities.get(category, []) if c.available]

        # Fallback: return all available
        return [c for caps in self.capabilities.values() for c in caps if c.available]

    def generate_compact_prompt(self) -> str:
        """
        Generate a compact LLM prompt with all capabilities.
        Optimized for minimal tokens while maintaining clarity.
        """
        lines = [
            "You are JARVIS, a voice assistant. Respond with TOOL calls or natural text.",
            "",
            "FORMAT: TOOL: name(param=\"value\")",
            "",
            "TOOLS:"
        ]

        for cat, info in self.CATEGORIES.items():
            caps = [c for c in self.capabilities.get(cat, []) if c.available]
            if not caps:
                continue

            lines.append(f"\n[{info['name']}]")
            for cap in caps:
                # Compact format: tool_name: triggers → example
                triggers = "/".join(cap.triggers[:3])
                lines.append(f"• {cap.tool_name} ({triggers})")

        lines.append("\nEXAMPLES:")

        # Add one example per category
        for cat in self.CATEGORIES:
            caps = [c for c in self.capabilities.get(cat, []) if c.available]
            if caps:
                cap = caps[0]
                lines.append(f'"{cap.example_input}" → {cap.example_output}')

        return "\n".join(lines)

    def generate_category_prompt(self, category: str) -> str:
        """Generate focused prompt for a specific category"""
        if category not in self.capabilities:
            return ""

        caps = [c for c in self.capabilities[category] if c.available]
        if not caps:
            return ""

        info = self.CATEGORIES.get(category, {})
        lines = [
            f"# {info.get('name', category)}",
            f"Description: {info.get('description', '')}",
            "",
            "Available tools:"
        ]

        for cap in caps:
            lines.append(f"\n## {cap.tool_name}")
            lines.append(f"Description: {cap.description}")
            lines.append(f"Triggers: {', '.join(cap.triggers)}")
            lines.append(f"Example: \"{cap.example_input}\" → {cap.example_output}")

        return "\n".join(lines)

    def generate_smart_prompt(self, user_input: str) -> str:
        """
        Generate an optimized prompt based on user input.
        Only includes relevant tools to reduce token usage.
        """
        category = self.detect_category(user_input)

        lines = [
            "You are JARVIS. Respond with a TOOL call.",
            "FORMAT: TOOL: name(param=\"value\")",
            ""
        ]

        if category:
            # Include primary category tools
            caps = [c for c in self.capabilities.get(category, []) if c.available]

            lines.append(f"RELEVANT TOOLS for your request:")
            for cap in caps:
                lines.append(f"• {cap.tool_name}: {cap.description}")
                lines.append(f"  Example: \"{cap.example_input}\" → {cap.example_output}")
        else:
            # Include all tools compactly
            lines.append("ALL TOOLS:")
            for cat, caps_list in self.capabilities.items():
                for cap in caps_list:
                    if cap.available:
                        lines.append(f"• {cap.tool_name}: {cap.triggers[0]}")

        return "\n".join(lines)

    def get_tool_list(self) -> List[str]:
        """Get list of all available tool names"""
        return [
            cap.tool_name
            for caps in self.capabilities.values()
            for cap in caps
            if cap.available
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Export manifest as dictionary"""
        return {
            "platform": {
                "distribution": self.platform.distribution.value,
                "audio": self.platform.audio_system.value,
                "display": self.platform.display_server.value,
                "desktop": self.platform.desktop_environment.value
            },
            "capabilities": {
                cat: [
                    {
                        "name": cap.name,
                        "tool": cap.tool_name,
                        "available": cap.available,
                        "triggers": cap.triggers
                    }
                    for cap in caps
                ]
                for cat, caps in self.capabilities.items()
            },
            "summary": {
                "total": self.count_capabilities(),
                "available": self.count_available()
            }
        }


# Singleton instance
_manifest: Optional[CapabilityManifest] = None


def get_manifest() -> CapabilityManifest:
    """Get or create the capability manifest"""
    global _manifest
    if _manifest is None:
        _manifest = CapabilityManifest()
    return _manifest
