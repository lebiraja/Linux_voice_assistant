"""
Intent Registry - Declarative action definitions inspired by Apple's App Intents.
This provides a unified way to define what JARVIS can do.
"""

import yaml
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class IntentCategory(Enum):
    """Categories of intents for organization"""
    APP_CONTROL = "app_control"
    SYSTEM_INFO = "system_info"
    SYSTEM_CONTROL = "system_control"
    MEDIA = "media"
    FILES = "files"
    WEB = "web"
    CONVERSATION = "conversation"
    AUTOMATION = "automation"
    USER_CONTEXT = "user_context"


@dataclass
class IntentParameter:
    """Parameter definition for an intent"""
    name: str
    type: str  # string, integer, boolean, float, enum
    description: str
    required: bool = True
    default: Any = None
    enum_values: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class Intent:
    """
    Declarative intent definition.

    An intent represents something JARVIS can do, with:
    - Natural language triggers that activate it
    - Parameters it needs
    - The tool that executes it
    - Examples for the LLM
    """
    name: str
    description: str
    category: IntentCategory
    triggers: List[str]  # Natural language patterns
    tool_name: str  # Tool to execute
    parameters: List[IntentParameter] = field(default_factory=list)
    examples: List[Dict[str, str]] = field(default_factory=list)  # input -> output
    requires: List[str] = field(default_factory=list)  # Required commands/tools
    platforms: List[str] = field(default_factory=lambda: ["all"])  # Platform restrictions

    def matches(self, text: str) -> float:
        """
        Check if text matches this intent.
        Returns confidence score 0.0 - 1.0
        """
        text_lower = text.lower()

        # Check exact trigger matches
        for trigger in self.triggers:
            if trigger.lower() in text_lower:
                # Weight by how much of the text the trigger covers
                coverage = len(trigger) / len(text)
                return min(0.5 + coverage * 0.5, 1.0)

        return 0.0

    def to_prompt_example(self) -> str:
        """Generate LLM prompt example for this intent"""
        if not self.examples:
            # Generate default example
            param_str = ", ".join(
                f'{p.name}="{p.examples[0] if p.examples else p.name}"'
                for p in self.parameters if p.required
            )
            return f'"{self.triggers[0]}" → TOOL: {self.tool_name}({param_str})'

        # Use first defined example
        ex = self.examples[0]
        return f'"{ex.get("input", self.triggers[0])}" → {ex.get("output", f"TOOL: {self.tool_name}()")}'


class IntentRegistry:
    """
    Central registry for all intents.
    Provides intent discovery, matching, and LLM prompt generation.
    """

    def __init__(self):
        self.intents: Dict[str, Intent] = {}
        self.by_category: Dict[IntentCategory, List[Intent]] = {
            cat: [] for cat in IntentCategory
        }
        self.by_tool: Dict[str, Intent] = {}

        logger.info("IntentRegistry initialized")

    def register(self, intent: Intent) -> None:
        """Register an intent"""
        self.intents[intent.name] = intent
        self.by_category[intent.category].append(intent)
        self.by_tool[intent.tool_name] = intent

        logger.debug(f"Registered intent: {intent.name} -> {intent.tool_name}")

    def register_all(self, intents: List[Intent]) -> None:
        """Register multiple intents"""
        for intent in intents:
            self.register(intent)

    def get(self, name: str) -> Optional[Intent]:
        """Get intent by name"""
        return self.intents.get(name)

    def get_by_tool(self, tool_name: str) -> Optional[Intent]:
        """Get intent by tool name"""
        return self.by_tool.get(tool_name)

    def get_by_category(self, category: IntentCategory) -> List[Intent]:
        """Get all intents in a category"""
        return self.by_category.get(category, [])

    def find_matching(self, text: str, threshold: float = 0.3) -> List[tuple]:
        """
        Find intents matching the given text.
        Returns list of (intent, confidence) tuples, sorted by confidence.
        """
        matches = []

        for intent in self.intents.values():
            confidence = intent.matches(text)
            if confidence >= threshold:
                matches.append((intent, confidence))

        # Sort by confidence descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def get_best_match(self, text: str) -> Optional[Intent]:
        """Get the best matching intent for text"""
        matches = self.find_matching(text)
        if matches:
            return matches[0][0]
        return None

    def generate_category_prompt(self, category: IntentCategory) -> str:
        """Generate LLM prompt for a specific category"""
        intents = self.by_category.get(category, [])
        if not intents:
            return ""

        lines = [f"## {category.value.replace('_', ' ').title()}"]

        for intent in intents:
            param_desc = ", ".join(
                f'{p.name}' + ('*' if p.required else '')
                for p in intent.parameters
            )
            lines.append(f"- {intent.tool_name}({param_desc}): {intent.description}")

        return "\n".join(lines)

    def generate_full_prompt(self) -> str:
        """Generate complete LLM prompt with all intents"""
        sections = []

        for category in IntentCategory:
            section = self.generate_category_prompt(category)
            if section:
                sections.append(section)

        return "\n\n".join(sections)

    def generate_examples_prompt(self, max_per_category: int = 2) -> str:
        """Generate examples section for LLM prompt"""
        lines = ["## Examples"]

        for category in IntentCategory:
            intents = self.by_category.get(category, [])
            for intent in intents[:max_per_category]:
                lines.append(intent.to_prompt_example())

        return "\n".join(lines)

    def get_compact_manifest(self) -> Dict:
        """
        Generate a compact manifest for capability awareness.
        This is what we teach the LLM about what JARVIS can do.
        """
        manifest = {
            "categories": {},
            "total_intents": len(self.intents),
            "capabilities": []
        }

        for category in IntentCategory:
            intents = self.by_category.get(category, [])
            if intents:
                manifest["categories"][category.value] = {
                    "count": len(intents),
                    "tools": [i.tool_name for i in intents],
                    "triggers": list(set(
                        trigger
                        for i in intents
                        for trigger in i.triggers[:2]  # Top 2 triggers per intent
                    ))
                }
                manifest["capabilities"].extend([
                    f"{category.value}: {i.description}"
                    for i in intents
                ])

        return manifest

    def load_from_yaml(self, yaml_path: Path) -> None:
        """Load intents from YAML file"""
        if not yaml_path.exists():
            logger.warning(f"Intent YAML not found: {yaml_path}")
            return

        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        for intent_data in data.get('intents', []):
            intent = Intent(
                name=intent_data['name'],
                description=intent_data['description'],
                category=IntentCategory(intent_data['category']),
                triggers=intent_data.get('triggers', []),
                tool_name=intent_data['tool'],
                parameters=[
                    IntentParameter(
                        name=p['name'],
                        type=p.get('type', 'string'),
                        description=p.get('description', ''),
                        required=p.get('required', True),
                        default=p.get('default'),
                        enum_values=p.get('enum', []),
                        examples=p.get('examples', [])
                    )
                    for p in intent_data.get('parameters', [])
                ],
                examples=intent_data.get('examples', []),
                requires=intent_data.get('requires', []),
                platforms=intent_data.get('platforms', ['all'])
            )
            self.register(intent)

        logger.info(f"Loaded {len(self.intents)} intents from {yaml_path}")


def create_default_intents() -> List[Intent]:
    """Create the default set of intents for JARVIS"""

    intents = [
        # ========== APP CONTROL ==========
        Intent(
            name="open_application",
            description="Launch an application",
            category=IntentCategory.APP_CONTROL,
            triggers=["open", "launch", "start", "run"],
            tool_name="open_app",
            parameters=[
                IntentParameter(
                    name="app_name",
                    type="string",
                    description="Name of the application to open",
                    required=True,
                    examples=["firefox", "terminal", "vscode", "spotify"]
                )
            ],
            examples=[
                {"input": "open firefox", "output": 'TOOL: open_app(app_name="firefox")'},
                {"input": "launch the terminal", "output": 'TOOL: open_app(app_name="terminal")'},
                {"input": "start vscode", "output": 'TOOL: open_app(app_name="vscode")'},
            ]
        ),
        Intent(
            name="close_application",
            description="Close a running application",
            category=IntentCategory.APP_CONTROL,
            triggers=["close", "quit", "exit", "kill", "stop"],
            tool_name="close_app",
            parameters=[
                IntentParameter(
                    name="app_name",
                    type="string",
                    description="Name of the application to close",
                    required=True,
                    examples=["firefox", "chrome", "spotify"]
                ),
                IntentParameter(
                    name="force",
                    type="boolean",
                    description="Force kill if graceful close fails",
                    required=False,
                    default=False
                )
            ],
            examples=[
                {"input": "close firefox", "output": 'TOOL: close_app(app_name="firefox")'},
                {"input": "kill chrome", "output": 'TOOL: close_app(app_name="chrome", force=true)'},
            ]
        ),

        # ========== SYSTEM INFO ==========
        Intent(
            name="get_cpu_usage",
            description="Get CPU usage percentage",
            category=IntentCategory.SYSTEM_INFO,
            triggers=["cpu", "processor", "cpu usage", "processor usage"],
            tool_name="get_system_info",
            parameters=[
                IntentParameter(
                    name="info_type",
                    type="enum",
                    description="Type of system info",
                    required=True,
                    default="cpu",
                    enum_values=["cpu", "memory", "disk", "all"]
                )
            ],
            examples=[
                {"input": "what's my CPU usage", "output": 'TOOL: get_system_info(info_type="cpu")'},
                {"input": "show CPU", "output": 'TOOL: get_system_info(info_type="cpu")'},
            ]
        ),
        Intent(
            name="get_memory_usage",
            description="Get RAM/memory usage",
            category=IntentCategory.SYSTEM_INFO,
            triggers=["ram", "memory", "ram usage", "memory usage"],
            tool_name="get_system_info",
            parameters=[
                IntentParameter(
                    name="info_type",
                    type="enum",
                    description="Type of system info",
                    required=True,
                    default="memory",
                    enum_values=["cpu", "memory", "disk", "all"]
                )
            ],
            examples=[
                {"input": "how much RAM am I using", "output": 'TOOL: get_system_info(info_type="memory")'},
                {"input": "show memory", "output": 'TOOL: get_system_info(info_type="memory")'},
            ]
        ),
        Intent(
            name="get_disk_usage",
            description="Get disk space information",
            category=IntentCategory.SYSTEM_INFO,
            triggers=["disk", "storage", "disk space", "storage space", "free space"],
            tool_name="get_system_info",
            parameters=[
                IntentParameter(
                    name="info_type",
                    type="enum",
                    description="Type of system info",
                    required=True,
                    default="disk",
                    enum_values=["cpu", "memory", "disk", "all"]
                )
            ],
            examples=[
                {"input": "how much disk space", "output": 'TOOL: get_system_info(info_type="disk")'},
                {"input": "show storage", "output": 'TOOL: get_system_info(info_type="disk")'},
            ]
        ),

        # ========== SYSTEM CONTROL ==========
        Intent(
            name="set_brightness",
            description="Control screen brightness",
            category=IntentCategory.SYSTEM_CONTROL,
            triggers=["brightness", "screen brightness", "display brightness"],
            tool_name="control_brightness",
            parameters=[
                IntentParameter(
                    name="action",
                    type="enum",
                    description="Brightness action",
                    required=True,
                    enum_values=["get", "set", "increase", "decrease"]
                ),
                IntentParameter(
                    name="value",
                    type="integer",
                    description="Brightness level 0-100",
                    required=False
                )
            ],
            examples=[
                {"input": "set brightness to 80", "output": 'TOOL: control_brightness(action="set", value=80)'},
                {"input": "increase brightness", "output": 'TOOL: control_brightness(action="increase")'},
                {"input": "dim the screen", "output": 'TOOL: control_brightness(action="decrease")'},
            ]
        ),
        Intent(
            name="set_volume",
            description="Control system volume",
            category=IntentCategory.SYSTEM_CONTROL,
            triggers=["volume", "sound", "audio level", "speaker"],
            tool_name="control_system_volume",
            parameters=[
                IntentParameter(
                    name="action",
                    type="enum",
                    description="Volume action",
                    required=True,
                    enum_values=["get", "set", "increase", "decrease", "mute", "unmute"]
                ),
                IntentParameter(
                    name="value",
                    type="integer",
                    description="Volume level 0-100",
                    required=False
                )
            ],
            examples=[
                {"input": "set volume to 50", "output": 'TOOL: control_system_volume(action="set", value=50)'},
                {"input": "turn up the volume", "output": 'TOOL: control_system_volume(action="increase")'},
                {"input": "mute", "output": 'TOOL: control_system_volume(action="mute")'},
            ]
        ),
        Intent(
            name="power_action",
            description="System power management",
            category=IntentCategory.SYSTEM_CONTROL,
            triggers=["shutdown", "restart", "reboot", "suspend", "sleep", "lock"],
            tool_name="power_management",
            parameters=[
                IntentParameter(
                    name="action",
                    type="enum",
                    description="Power action",
                    required=True,
                    enum_values=["shutdown", "reboot", "suspend", "lock"]
                ),
                IntentParameter(
                    name="confirm",
                    type="boolean",
                    description="Confirmation for destructive actions",
                    required=False,
                    default=False
                )
            ],
            examples=[
                {"input": "lock the screen", "output": 'TOOL: power_management(action="lock")'},
                {"input": "put computer to sleep", "output": 'TOOL: power_management(action="suspend")'},
            ]
        ),

        # ========== MEDIA CONTROL ==========
        Intent(
            name="media_playback",
            description="Control media playback",
            category=IntentCategory.MEDIA,
            triggers=["play", "pause", "stop", "next", "previous", "skip"],
            tool_name="control_media",
            parameters=[
                IntentParameter(
                    name="action",
                    type="enum",
                    description="Playback action",
                    required=True,
                    enum_values=["play", "pause", "play-pause", "stop", "next", "previous"]
                )
            ],
            examples=[
                {"input": "play music", "output": 'TOOL: control_media(action="play")'},
                {"input": "pause", "output": 'TOOL: control_media(action="pause")'},
                {"input": "next song", "output": 'TOOL: control_media(action="next")'},
                {"input": "skip this track", "output": 'TOOL: control_media(action="next")'},
            ],
            requires=["playerctl"]
        ),
        Intent(
            name="now_playing",
            description="Get current playing track info",
            category=IntentCategory.MEDIA,
            triggers=["what's playing", "current song", "now playing", "what song"],
            tool_name="get_now_playing",
            parameters=[],
            examples=[
                {"input": "what's playing", "output": 'TOOL: get_now_playing()'},
                {"input": "what song is this", "output": 'TOOL: get_now_playing()'},
            ],
            requires=["playerctl"]
        ),

        # ========== WEB ==========
        Intent(
            name="web_search",
            description="Search the web",
            category=IntentCategory.WEB,
            triggers=["search", "google", "look up", "find online"],
            tool_name="search_web",
            parameters=[
                IntentParameter(
                    name="query",
                    type="string",
                    description="Search query",
                    required=True,
                    examples=["python tutorial", "weather today"]
                )
            ],
            examples=[
                {"input": "search for python tutorials", "output": 'TOOL: search_web(query="python tutorials")'},
                {"input": "google docker installation", "output": 'TOOL: search_web(query="docker installation")'},
            ]
        ),
        Intent(
            name="open_website",
            description="Open a website",
            category=IntentCategory.WEB,
            triggers=["open", "go to", "visit", "browse"],
            tool_name="open_website",
            parameters=[
                IntentParameter(
                    name="website",
                    type="string",
                    description="Website name or URL",
                    required=True,
                    examples=["google", "github", "youtube", "gmail"]
                )
            ],
            examples=[
                {"input": "open youtube", "output": 'TOOL: open_website(website="youtube")'},
                {"input": "go to github", "output": 'TOOL: open_website(website="github")'},
                {"input": "check my email", "output": 'TOOL: open_website(website="gmail")'},
            ]
        ),

        # ========== FILES ==========
        Intent(
            name="list_files",
            description="List files in a directory",
            category=IntentCategory.FILES,
            triggers=["list files", "show files", "what files", "ls", "directory"],
            tool_name="list_files",
            parameters=[
                IntentParameter(
                    name="path",
                    type="string",
                    description="Directory path",
                    required=False,
                    default="."
                ),
                IntentParameter(
                    name="pattern",
                    type="string",
                    description="File pattern (e.g., *.py)",
                    required=False
                )
            ],
            examples=[
                {"input": "list files here", "output": 'TOOL: list_files(path=".")'},
                {"input": "show python files", "output": 'TOOL: list_files(pattern="*.py")'},
            ]
        ),
        Intent(
            name="read_file",
            description="Read contents of a file",
            category=IntentCategory.FILES,
            triggers=["read", "show", "cat", "display", "contents of"],
            tool_name="read_file",
            parameters=[
                IntentParameter(
                    name="file_path",
                    type="string",
                    description="Path to the file",
                    required=True
                )
            ],
            examples=[
                {"input": "read config.yaml", "output": 'TOOL: read_file(file_path="config.yaml")'},
                {"input": "show me the readme", "output": 'TOOL: read_file(file_path="README.md")'},
            ]
        ),

        # ========== CONVERSATION ==========
        Intent(
            name="answer_question",
            description="Answer a general question",
            category=IntentCategory.CONVERSATION,
            triggers=["what is", "what are", "how does", "explain", "tell me about", "who is"],
            tool_name="answer_question",
            parameters=[
                IntentParameter(
                    name="question",
                    type="string",
                    description="The question to answer",
                    required=True
                )
            ],
            examples=[
                {"input": "what is Docker", "output": 'TOOL: answer_question(question="What is Docker?")'},
                {"input": "how does Git work", "output": 'TOOL: answer_question(question="How does Git work?")'},
            ]
        ),
        Intent(
            name="casual_chat",
            description="Have a casual conversation",
            category=IntentCategory.CONVERSATION,
            triggers=["hello", "hi", "hey", "good morning", "how are you", "thanks"],
            tool_name="have_conversation",
            parameters=[
                IntentParameter(
                    name="message",
                    type="string",
                    description="The message/greeting",
                    required=True
                )
            ],
            examples=[
                {"input": "hello", "output": 'TOOL: have_conversation(message="hello")'},
                {"input": "how are you", "output": 'TOOL: have_conversation(message="how are you")'},
            ]
        ),

        # ========== AUTOMATION ==========
        Intent(
            name="generate_script",
            description="Generate and run a custom script",
            category=IntentCategory.AUTOMATION,
            triggers=["create script", "write script", "generate script", "make a script",
                      "automate", "script for", "code to"],
            tool_name="generate_and_run_script",
            parameters=[
                IntentParameter(
                    name="task_description",
                    type="string",
                    description="What the script should do",
                    required=True
                ),
                IntentParameter(
                    name="language",
                    type="enum",
                    description="Programming language",
                    required=False,
                    default="bash",
                    enum_values=["bash", "python", "javascript"]
                ),
                IntentParameter(
                    name="auto_execute",
                    type="boolean",
                    description="Execute immediately",
                    required=False,
                    default=True
                )
            ],
            examples=[
                {"input": "create a script to backup my documents",
                 "output": 'TOOL: generate_and_run_script(task_description="backup my documents")'},
                {"input": "write a python script to download images",
                 "output": 'TOOL: generate_and_run_script(task_description="download images", language="python")'},
            ]
        ),
        Intent(
            name="run_command",
            description="Execute a shell command",
            category=IntentCategory.AUTOMATION,
            triggers=["run", "execute", "command"],
            tool_name="run_script",
            parameters=[
                IntentParameter(
                    name="script",
                    type="string",
                    description="Shell command to run",
                    required=True
                )
            ],
            examples=[
                {"input": "run ls -la", "output": 'TOOL: run_script(script="ls -la")'},
                {"input": "execute git status", "output": 'TOOL: run_script(script="git status")'},
            ]
        ),
    ]

    return intents


def create_registry_with_defaults() -> IntentRegistry:
    """Create an IntentRegistry with all default intents registered"""
    registry = IntentRegistry()
    registry.register_all(create_default_intents())
    logger.info(f"Created registry with {len(registry.intents)} default intents")
    return registry
