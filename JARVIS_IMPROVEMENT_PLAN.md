# JARVIS Voice AI Assistant - Complete Improvement Plan

## Executive Summary

This document provides a comprehensive analysis of the JARVIS voice assistant project, identifies all issues, and proposes an architectural redesign inspired by modern voice assistant systems (like Apple's Siri 2026 architecture).

---

## 1. COMPLETE CAPABILITY INVENTORY

### All Available Tools (26 Total)

#### Application Control
| Tool | Function | Parameters | Example |
|------|----------|------------|---------|
| `open_app` | Launch applications | `app_name` (required) | `TOOL: open_app(app_name="firefox")` |
| `close_app` | Close running apps | `app_name`, `force` | `TOOL: close_app(app_name="terminal")` |
| `run_script` | Execute shell scripts | `script`, `working_dir` | `TOOL: run_script(script="mkdir test")` |

#### System Information
| Tool | Function | Parameters | Example |
|------|----------|------------|---------|
| `get_system_info` | CPU/RAM/disk usage | `info_type` (cpu/memory/disk/all) | `TOOL: get_system_info(info_type="cpu")` |
| `get_processes` | List running processes | `filter_name`, `limit` | `TOOL: get_processes(filter_name="chrome")` |
| `execute_command` | Run whitelisted commands | `command` | `TOOL: execute_command(command="ls -la")` |

#### System Control
| Tool | Function | Parameters | Example |
|------|----------|------------|---------|
| `control_brightness` | Screen brightness | `action`, `value` | `TOOL: control_brightness(action="set", value=80)` |
| `control_system_volume` | System volume | `action`, `value` | `TOOL: control_system_volume(action="set", value=50)` |
| `power_management` | Power actions | `action`, `confirm` | `TOOL: power_management(action="suspend")` |

#### Media Control
| Tool | Function | Parameters | Example |
|------|----------|------------|---------|
| `control_media` | Playback control | `action`, `value` | `TOOL: control_media(action="play")` |
| `get_now_playing` | Current track info | None | `TOOL: get_now_playing()` |

#### File System
| Tool | Function | Parameters | Example |
|------|----------|------------|---------|
| `list_files` | Directory listing | `path`, `pattern`, `recursive` | `TOOL: list_files(path=".", pattern="*.py")` |
| `read_file` | Read file content | `file_path`, `max_lines` | `TOOL: read_file(file_path="config.yaml")` |
| `search_files` | Find files | `path`, `pattern` | `TOOL: search_files(path=".", pattern="test")` |

#### Web Operations
| Tool | Function | Parameters | Example |
|------|----------|------------|---------|
| `search_web` | DuckDuckGo search | `query`, `max_results` | `TOOL: search_web(query="python tutorial")` |
| `fetch_url` | Get webpage content | `url`, `max_chars` | `TOOL: fetch_url(url="https://example.com")` |
| `open_website` | Open sites by name | `website` | `TOOL: open_website(website="github")` |
| `web_search` | Search on sites | `query`, `engine` | `TOOL: web_search(query="docker", engine="youtube")` |

#### AI Script Generation
| Tool | Function | Parameters | Example |
|------|----------|------------|---------|
| `generate_and_run_script` | AI creates scripts | `task_description`, `language`, `auto_execute` | `TOOL: generate_and_run_script(task_description="backup documents")` |

#### Conversation
| Tool | Function | Parameters | Example |
|------|----------|------------|---------|
| `answer_question` | Q&A responses | `question`, `topic`, `style` | `TOOL: answer_question(question="What is Docker?")` |
| `explain_concept` | Technical explanations | `concept`, `complexity` | `TOOL: explain_concept(concept="quantum computing")` |
| `have_conversation` | Casual chat | `message`, `conversation_type` | `TOOL: have_conversation(message="hello")` |

#### User Context
| Tool | Function | Parameters | Example |
|------|----------|------------|---------|
| `set_user_preference` | Remember preferences | `category`, `preference`, `value` | `TOOL: set_user_preference(category="response", preference="style", value="concise")` |
| `remember_user_info` | Store user info | `info_type`, `value` | `TOOL: remember_user_info(info_type="name", value="John")` |
| `set_work_context` | Track work context | `context_type`, `value` | `TOOL: set_work_context(context_type="project", value="web-app")` |

---

## 2. IDENTIFIED ISSUES

### Critical Issues

#### 2.1 TTS Issues
1. **Google TTS requires internet** - No offline fallback
2. **MP3 playback** - soundfile may not support MP3 without ffmpeg
3. **No error recovery** - Silent failure if TTS fails
4. **Config mismatch** - config.yaml mentions Piper but main.py uses GoogleTTS

#### 2.2 Tool Calling Issues
1. **Regex parsing fragility** - `TOOL: name(params)` format easily breaks
2. **No multi-step tool chaining** - Can't use output of one tool as input to another
3. **Limited error context** - Errors don't explain what went wrong to user
4. **Thinking tag removal** - Works but `<think>` handling is inconsistent
5. **Tool validation not robust** - Missing parameter defaults cause failures

#### 2.3 Cross-Platform Issues (Ubuntu vs Arch)
| Component | Ubuntu/GNOME | Arch/Wayland | Issue |
|-----------|--------------|--------------|-------|
| Audio Socket | `/run/user/1000/pulse` | `/run/user/1000/pipewire-0` | Hardcoded path |
| Display | X11 via /tmp/.X11-unix | Wayland (no X11 socket) | Hotkeys fail |
| Hotkeys | pynput works | pynput requires X11 | No Wayland support |
| xhost | Works | XWayland only | Pure Wayland breaks |

#### 2.4 LLM Integration Issues
1. **Prompt too long** - All 26 tools listed causing context bloat
2. **No tool categorization** - LLM struggles to pick the right tool
3. **Temperature too high for tool calls** - Should be 0.1-0.2 for reliability
4. **No few-shot examples** - LLM guesses tool format incorrectly

#### 2.5 Architecture Issues
1. **Monolithic design** - main.py does too much
2. **No intent disambiguation** - "volume up" could be system or media
3. **No capability discovery** - LLM doesn't know what's installed/available
4. **No sandbox** - Scripts run with full user permissions

---

## 3. PROPOSED ARCHITECTURE (Siri-Inspired)

### 3.1 Intent-Based Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        JARVIS Core                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Voice Input  │  │   Intent     │  │  Capability          │  │
│  │   Pipeline   │→ │   Router     │→ │  Registry            │  │
│  │ (STT)        │  │ (LLM-based)  │  │ (All available tools)│  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│         │                 │                     │               │
│         ↓                 ↓                     ↓               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Context    │  │   Intent     │  │    Action            │  │
│  │   Manager    │← │   Resolver   │→ │    Executor          │  │
│  │ (Memory)     │  │ (Maps to tool)│  │ (Sandboxed)          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                           │                     │               │
│                           ↓                     ↓               │
│                    ┌──────────────────────────────────┐        │
│                    │      Response Generator           │        │
│                    │      (TTS + Confirmation)         │        │
│                    └──────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Intent Registry (Like App Intents)

```python
# New declarative intent system
class Intent:
    """Declarative action definition"""
    name: str           # "open_application"
    description: str    # "Launch an application"
    triggers: list      # ["open", "launch", "start", "run"]
    parameters: list    # [Param("app_name", required=True)]
    handler: callable   # Function to execute
    category: str       # "app_control"
    platform: list      # ["linux", "wayland", "x11"]
```

### 3.3 Capability Manifest

Instead of listing 26 tools in the prompt, create a dynamic manifest:

```python
class CapabilityManifest:
    """Teaches LLM what JARVIS can do"""

    def __init__(self):
        self.categories = {
            "app_control": ["open", "close", "launch"],
            "system_info": ["cpu", "memory", "disk", "battery"],
            "system_control": ["volume", "brightness", "power"],
            "media": ["play", "pause", "next", "previous"],
            "web": ["search", "open website", "fetch"],
            "files": ["list", "read", "search", "find"],
            "conversation": ["question", "explain", "chat"],
            "automation": ["script", "generate", "execute"]
        }

    def get_relevant_tools(self, user_input: str) -> list:
        """Return only relevant tools for the given input"""
        # Semantic matching to reduce context
        pass

    def generate_compact_prompt(self, category: str) -> str:
        """Generate focused prompt for specific category"""
        pass
```

### 3.4 Sandboxed Execution

```python
class SandboxExecutor:
    """Safe script execution environment"""

    def __init__(self):
        self.allowed_paths = ["/tmp", "~/.cache/jarvis"]
        self.blocked_commands = ["rm -rf", "mkfs", "dd", ">dev/"]
        self.timeout = 30
        self.max_memory = "512M"

    def execute(self, script: str, language: str) -> dict:
        """Run script in isolated environment"""
        # Use firejail, bubblewrap, or containers
        pass
```

---

## 4. IMPLEMENTATION PLAN

### Phase 1: Fix Critical Issues (Immediate)

#### 1.1 Fix TTS Pipeline
- Add MP3 support via pydub/ffmpeg
- Add offline Piper TTS fallback
- Add graceful error handling
- Fix config.yaml/code mismatch

#### 1.2 Fix Tool Calling
- Improve regex parser robustness
- Add parameter type validation
- Add default parameter injection
- Better error messages to LLM

#### 1.3 Cross-Platform Compatibility
- Auto-detect audio system (PulseAudio/PipeWire)
- Auto-detect display server (X11/Wayland/XWayland)
- Use platform-appropriate hotkey capture
- Dynamic socket path configuration

### Phase 2: Architecture Improvements

#### 2.1 Intent Registry System
- Create declarative intent definitions
- Build intent-to-tool mapper
- Add disambiguation for overlapping intents
- Support multi-step intents

#### 2.2 Improved LLM Integration
- Reduce prompt size with categorized tools
- Add few-shot examples
- Lower temperature for tool calls (0.1)
- Add chain-of-thought for complex tasks

#### 2.3 Context Management
- Semantic understanding of "it", "that"
- Session memory (10 exchanges)
- User preference learning
- Project/work context tracking

### Phase 3: Advanced Features

#### 3.1 Sandbox Execution
- Implement firejail wrapper for scripts
- Add resource limits
- Audit trail for executed commands
- Rollback capability for file changes

#### 3.2 Screen Awareness (Future)
- Capture current window title
- Understand clipboard content
- Context from active application
- "this" and "here" understanding

---

## 5. FILE STRUCTURE CHANGES

### Current Structure
```
linux-voice-ai/
├── main.py              # Monolithic - too many responsibilities
├── llm/
│   ├── prompts.py       # Static prompts
│   └── router.py        # Basic routing
├── tools/
│   ├── base.py
│   ├── registry.py
│   └── builtin/         # All tools flat
```

### Proposed Structure
```
linux-voice-ai/
├── core/
│   ├── jarvis.py           # Main orchestrator
│   ├── intent_router.py    # Intent detection & routing
│   └── context_manager.py  # Session & user context
├── intents/
│   ├── registry.py         # Intent registry
│   ├── resolver.py         # Intent disambiguation
│   └── definitions/        # Declarative intent YAML files
│       ├── app_control.yaml
│       ├── system_control.yaml
│       ├── media.yaml
│       └── web.yaml
├── capabilities/
│   ├── manifest.py         # Dynamic capability discovery
│   ├── platform.py         # Platform detection
│   └── tools/              # Categorized tools
│       ├── apps/
│       ├── system/
│       ├── media/
│       ├── web/
│       ├── files/
│       └── automation/
├── execution/
│   ├── executor.py         # Safe execution layer
│   ├── sandbox.py          # Sandboxed script runner
│   └── validators.py       # Input validation
├── llm/
│   ├── client.py           # Ollama client
│   ├── prompts.py          # Dynamic prompt builder
│   └── tool_selector.py    # Smart tool selection
├── audio/
│   ├── recorder.py
│   ├── player.py
│   └── platform/
│       ├── pulseaudio.py
│       └── pipewire.py
├── tts/
│   ├── engine.py           # TTS interface
│   ├── google_tts.py       # Online
│   └── piper_tts.py        # Offline
├── stt/
│   ├── whisper_engine.py
│   └── wake_word.py
├── input/
│   ├── hotkey.py           # Hotkey handler
│   └── platform/
│       ├── x11.py
│       └── wayland.py      # Wayland input capture
└── config/
    ├── config.yaml
    ├── intents.yaml        # Intent definitions
    └── platforms.yaml      # Platform-specific configs
```

---

## 6. IMMEDIATE CODE FIXES

### Fix 1: TTS Error Handling
```python
# tts/engine.py - New unified TTS interface
class TTSEngine:
    def __init__(self, config):
        self.primary = GoogleTTS(...)
        self.fallback = PiperTTS(...)

    def speak(self, text: str) -> Path:
        try:
            return self.primary.speak(text)
        except Exception as e:
            logger.warning(f"Primary TTS failed: {e}, using fallback")
            return self.fallback.speak(text)
```

### Fix 2: Robust Tool Parsing
```python
def parse_tool_call(response: str) -> dict:
    """More robust tool call parser"""
    # Clean thinking tags
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)

    # Multiple format support
    patterns = [
        r'TOOL:\s*(\w+)\((.*?)\)',  # TOOL: name(params)
        r'```tool\s+(\w+)\((.*?)\)```',  # Markdown code block
        r'\[CALL:\s*(\w+)\((.*?)\)\]',  # [CALL: name(params)]
    ]

    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return parse_params(match.group(1), match.group(2))

    return None
```

### Fix 3: Platform Detection
```python
# capabilities/platform.py
class PlatformDetector:
    @staticmethod
    def detect_audio_system() -> str:
        if Path("/run/user/1000/pipewire-0").exists():
            return "pipewire"
        if Path("/run/user/1000/pulse/native").exists():
            return "pulseaudio"
        return "alsa"

    @staticmethod
    def detect_display_server() -> str:
        if os.environ.get("WAYLAND_DISPLAY"):
            return "wayland"
        if os.environ.get("DISPLAY"):
            return "x11"
        return "headless"

    @staticmethod
    def get_audio_socket() -> str:
        system = PlatformDetector.detect_audio_system()
        uid = os.getuid()
        if system == "pipewire":
            return f"/run/user/{uid}/pipewire-0"
        return f"/run/user/{uid}/pulse/native"
```

---

## 7. IMPROVED LLM PROMPT

### New Compact Prompt System
```python
JARVIS_SYSTEM_PROMPT = """You are JARVIS, a voice assistant for Linux.

RESPONSE FORMAT:
For actions: TOOL: tool_name(param="value")
For conversation: Just respond naturally.

CATEGORIES:
1. Apps: open_app, close_app, run_script
2. System: get_system_info, control_brightness, control_volume, power_management
3. Media: control_media, get_now_playing
4. Web: search_web, open_website, web_search
5. Files: list_files, read_file, search_files
6. Chat: answer_question, explain_concept, have_conversation
7. Automation: generate_and_run_script

EXAMPLES:
"open firefox" → TOOL: open_app(app_name="firefox")
"what's CPU usage" → TOOL: get_system_info(info_type="cpu")
"play music" → TOOL: control_media(action="play")
"what is Docker" → TOOL: answer_question(question="What is Docker?")
"hello" → Hello! How can I help you today?
"""
```

---

## 8. WAYLAND COMPATIBILITY

### Option 1: Use evdev for Hotkeys
```python
# input/platform/wayland.py
import evdev
from evdev import InputDevice, categorize, ecodes

class WaylandHotkey:
    def __init__(self, key_combo, callback):
        self.devices = [InputDevice(path) for path in evdev.list_devices()]
        self.keyboard = self._find_keyboard()
        self.callback = callback

    def _find_keyboard(self):
        for device in self.devices:
            if ecodes.EV_KEY in device.capabilities():
                return device
        return None

    def listen(self):
        for event in self.keyboard.read_loop():
            if event.type == ecodes.EV_KEY:
                # Check for Ctrl+Space
                pass
```

### Option 2: Use dbus portal (Recommended)
```python
# For GNOME/KDE on Wayland
import dbus

class WaylandPortalHotkey:
    def __init__(self):
        self.bus = dbus.SessionBus()
        # Use xdg-desktop-portal for global shortcuts
```

---

## 9. TESTING CHECKLIST

### TTS Testing
- [ ] Google TTS works with internet
- [ ] Piper TTS works offline
- [ ] Fallback triggers correctly
- [ ] MP3 files play correctly
- [ ] WAV files play correctly

### Tool Calling Testing
- [ ] All 26 tools can be called
- [ ] Parameters parse correctly
- [ ] Default parameters work
- [ ] Error handling works
- [ ] Multi-tool responses parse

### Platform Testing
- [ ] Ubuntu 22.04 + GNOME (X11)
- [ ] Ubuntu 24.04 + GNOME (Wayland)
- [ ] Arch + KDE (Wayland)
- [ ] Arch + GNOME (Wayland)
- [ ] Arch + Sway (Wayland)

### Audio Testing
- [ ] Recording works (PulseAudio)
- [ ] Recording works (PipeWire)
- [ ] Playback works (PulseAudio)
- [ ] Playback works (PipeWire)

---

## 10. DEPENDENCIES TO ADD

```txt
# requirements.txt additions
pydub>=0.25.1          # Audio format conversion
evdev>=1.6.0           # Wayland keyboard input
firejail>=0.9.72       # Sandboxed execution (optional)
pyyaml>=6.0            # Intent definitions
```

---

## Summary

This plan addresses the core issues:
1. **TTS Issues** → Unified engine with fallbacks
2. **Tool Calling** → Robust parsing + categorization
3. **Cross-Platform** → Platform detection + adaptive config
4. **Architecture** → Intent-based declarative system
5. **Sandbox** → Safe script execution
6. **LLM Prompts** → Compact, categorized, few-shot

The redesign takes inspiration from Apple's Siri architecture while remaining practical for the current codebase scale.
