# JARVIS Capability Knowledge Base

This document serves as the complete reference for JARVIS's capabilities.
It's designed to be loaded into the LLM context for comprehensive understanding.

---

## What JARVIS Can Do

JARVIS is a voice-controlled AI assistant for Linux systems. It can:

### 1. Application Control
- **Open Applications**: Launch any installed application
  - Command: "open firefox", "launch terminal", "start vscode"
  - Tool: `open_app(app_name="firefox")`
  - Supports: All installed apps, smart name matching

- **Close Applications**: Terminate running applications
  - Command: "close chrome", "quit spotify", "kill terminal"
  - Tool: `close_app(app_name="chrome", force=false)`
  - Force option for unresponsive apps

### 2. System Information
- **CPU Usage**: Current processor utilization
  - Command: "what's my CPU usage", "show CPU"
  - Tool: `get_system_info(info_type="cpu")`
  - Returns: Usage %, core count, frequency

- **Memory Usage**: RAM utilization
  - Command: "how much RAM am I using", "memory usage"
  - Tool: `get_system_info(info_type="memory")`
  - Returns: Used/Total GB, percentage

- **Disk Usage**: Storage space
  - Command: "disk space", "how much storage"
  - Tool: `get_system_info(info_type="disk")`
  - Returns: Free/Used/Total GB

- **Running Processes**: Active tasks
  - Command: "what processes are running", "show processes"
  - Tool: `get_processes(filter_name="", limit=10)`

### 3. System Control
- **Screen Brightness**: Adjust display brightness
  - Command: "set brightness to 80", "dim the screen", "brightness up"
  - Tool: `control_brightness(action="set", value=80)`
  - Actions: get, set, increase, decrease
  - Range: 0-100

- **System Volume**: Control audio output
  - Command: "volume 50", "mute", "turn up the volume"
  - Tool: `control_system_volume(action="set", value=50)`
  - Actions: get, set, increase, decrease, mute, unmute
  - Range: 0-100

- **Power Management**: System power actions
  - Command: "lock the screen", "suspend", "restart"
  - Tool: `power_management(action="lock")`
  - Actions: lock, suspend, shutdown, reboot
  - Note: shutdown/reboot require confirmation

### 4. Media Control
- **Playback Control**: Control media players
  - Command: "play music", "pause", "next song", "skip"
  - Tool: `control_media(action="play")`
  - Actions: play, pause, play-pause, stop, next, previous
  - Works with: Spotify, VLC, Firefox, Chrome, etc.

- **Now Playing**: Current track information
  - Command: "what's playing", "what song is this"
  - Tool: `get_now_playing()`
  - Returns: Title, artist, album, duration

- **Media Volume**: Player-specific volume
  - Command: "media volume up", "set media volume to 80"
  - Tool: `control_media(action="set-volume", value=80)`

### 5. File Operations
- **List Files**: View directory contents
  - Command: "list files", "show python files", "what files are here"
  - Tool: `list_files(path=".", pattern="*.py", recursive=false)`
  - Supports glob patterns

- **Read Files**: View file contents
  - Command: "read config.yaml", "show me the readme"
  - Tool: `read_file(file_path="config.yaml", max_lines=100)`
  - Text files only

- **Search Files**: Find files by pattern
  - Command: "find all test files", "search for images"
  - Tool: `search_files(path=".", pattern="*test*")`
  - Recursive search

### 6. Web Operations
- **Web Search**: Search the internet
  - Command: "search for python tutorial", "google docker installation"
  - Tool: `search_web(query="python tutorial")`
  - Uses DuckDuckGo

- **Open Websites**: Quick access to sites
  - Command: "open youtube", "go to github", "check email"
  - Tool: `open_website(website="youtube")`
  - Supported: google, gmail, youtube, github, facebook, twitter, netflix, spotify, stackoverflow, wikipedia

- **Site-Specific Search**: Search within sites
  - Command: "search youtube for music", "search github for python"
  - Tool: `web_search(query="music", engine="youtube")`
  - Engines: google, youtube, wikipedia, github, stackoverflow

### 7. Automation & Scripts
- **AI Script Generation**: Let AI write and run scripts
  - Command: "create a script to backup my documents"
  - Tool: `generate_and_run_script(task_description="backup documents", language="bash", auto_execute=true)`
  - Languages: bash, python, javascript

- **Run Commands**: Execute shell commands
  - Command: "run git status", "execute ls -la"
  - Tool: `run_script(script="git status")`
  - Safety: Dangerous commands blocked

### 8. Conversation & Knowledge
- **Answer Questions**: General Q&A
  - Command: "what is Docker", "how does Git work"
  - Tool: `answer_question(question="What is Docker?")`

- **Explain Concepts**: Technical explanations
  - Command: "explain machine learning", "what is an API"
  - Tool: `explain_concept(concept="machine learning", complexity="simple")`
  - Complexity: simple, intermediate, advanced

- **Casual Chat**: Friendly conversation
  - Command: "hello", "how are you", "thanks"
  - Tool: `have_conversation(message="hello")`

### 9. User Context & Memory
- **Remember Preferences**: Store user preferences
  - Command: "I prefer concise responses"
  - Tool: `set_user_preference(category="response", preference="style", value="concise")`

- **Remember Info**: Store user information
  - Command: "my name is John", "I'm in New York"
  - Tool: `remember_user_info(info_type="name", value="John")`

- **Work Context**: Track current project
  - Command: "I'm working on the web app project"
  - Tool: `set_work_context(context_type="project", value="web-app")`

---

## Tool Call Format

JARVIS uses a simple text-based format:
```
TOOL: tool_name(param1="value", param2=123, param3=true)
```

### Parameter Types
- **Strings**: Always quoted - `param="value"`
- **Numbers**: No quotes - `param=123`
- **Booleans**: Lowercase - `param=true` or `param=false`

### Examples
```
TOOL: open_app(app_name="firefox")
TOOL: get_system_info(info_type="cpu")
TOOL: control_brightness(action="set", value=80)
TOOL: control_media(action="play")
TOOL: answer_question(question="What is Python?")
```

---

## Platform Support

### Linux Distributions
- Ubuntu (20.04+)
- Debian
- Arch Linux
- Manjaro
- Fedora
- openSUSE

### Display Servers
- X11 (full support)
- XWayland (full support)
- Wayland (limited hotkey support)

### Desktop Environments
- GNOME
- KDE Plasma
- XFCE
- Sway
- i3
- Hyprland

### Audio Systems
- PulseAudio
- PipeWire
- ALSA

---

## Smart Understanding

JARVIS understands natural language variations:

| User Says | JARVIS Understands |
|-----------|---------------------|
| "open firefox" | Launch Firefox browser |
| "launch the browser" | Open default browser |
| "what's my CPU at" | Get CPU usage percentage |
| "how's the processor" | Get CPU information |
| "play some music" | Resume media playback |
| "next track" | Skip to next song |
| "dim the screen" | Decrease brightness |
| "make it brighter" | Increase brightness |
| "close everything" | Close all applications |
| "check my email" | Open Gmail |

---

## Error Handling

JARVIS handles errors gracefully:

1. **Unknown App**: "I couldn't find that application. Is it installed?"
2. **No Audio**: "I didn't hear anything. Please try again."
3. **LLM Timeout**: Falls back to rule-based parsing
4. **Tool Failure**: Provides specific error message
5. **Unsafe Command**: Blocks dangerous operations

---

## Tips for Best Results

1. **Be Clear**: "Open Firefox" is better than "browser"
2. **Be Specific**: "Set brightness to 80" vs "change brightness"
3. **Use Natural Language**: Speak as you would to a person
4. **Wait for Confirmation**: Let JARVIS confirm actions
5. **Use Wake Word**: Say "Hey JARVIS" for hands-free use
