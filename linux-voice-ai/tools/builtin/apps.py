"""
Application control tools for launching and managing apps dynamically
"""

import subprocess
import shutil
import logging
from typing import Dict, Any
from ..base import Tool, ToolParameter

logger = logging.getLogger(__name__)


class OpenAppTool(Tool):
    """
    Open/launch any application by name.
    Uses which/whereis to find apps, or tries common locations.
    """
    
    name = "open_app"
    description = "Open or launch any application by name. Works for terminal, firefox, chrome, vscode, nautilus, or any installed app."
    parameters = [
        ToolParameter(
            name="app_name",
            type="string",
            description="Name of the application to open (e.g., 'terminal', 'firefox', 'nautilus', 'code')",
            required=True
        )
    ]
    
    # Common app name aliases
    APP_ALIASES = {
        # Terminal emulators
        "terminal": ["gnome-terminal", "konsole", "xfce4-terminal", "xterm", "terminator", "alacritty", "kitty"],
        "term": ["gnome-terminal", "konsole", "xfce4-terminal", "xterm"],
        # File managers
        "file manager": ["nautilus", "dolphin", "thunar", "nemo", "pcmanfm"],
        "files": ["nautilus", "dolphin", "thunar", "nemo"],
        "nautilus": ["nautilus", "org.gnome.Nautilus"],
        # Browsers
        "browser": ["firefox", "google-chrome", "chromium", "brave-browser"],
        "chrome": ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"],
        "firefox": ["firefox", "firefox-esr"],
        # Code editors
        "code": ["code", "codium", "code-oss"],
        "vscode": ["code", "codium", "code-oss"],
        "sublime": ["subl", "sublime_text"],
        "gedit": ["gedit", "org.gnome.gedit"],
        # System
        "settings": ["gnome-control-center", "systemsettings", "xfce4-settings-manager"],
        "calculator": ["gnome-calculator", "kcalc", "galculator"],
        "text editor": ["gedit", "kate", "mousepad", "xed"],
        # Media
        "music": ["rhythmbox", "spotify", "vlc", "audacious"],
        "video": ["vlc", "totem", "mpv", "celluloid"],
        "spotify": ["spotify", "flatpak run com.spotify.Client"],
        # Communication
        "slack": ["slack", "flatpak run com.slack.Slack"],
        "discord": ["discord", "flatpak run com.discordapp.Discord"],
        # Office
        "libreoffice": ["libreoffice", "soffice"],
        "writer": ["libreoffice --writer", "soffice --writer"],
    }
    
    def execute(self, app_name: str) -> Dict[str, Any]:
        """Open an application by name."""
        app_name = app_name.lower().strip()
        
        # Get possible executables for this app
        executables = self._get_executables(app_name)
        
        # Try each executable until one works
        for exe in executables:
            if self._try_launch(exe):
                return {
                    "success": True,
                    "app": app_name,
                    "executable": exe,
                    "message": f"Launched {app_name}"
                }
        
        return {
            "success": False,
            "app": app_name,
            "error": f"Could not find or launch '{app_name}'. Make sure it's installed.",
            "tried": executables[:5]
        }
    
    def _get_executables(self, app_name: str) -> list:
        """Get list of possible executables for an app name."""
        executables = []
        
        # Check aliases first
        if app_name in self.APP_ALIASES:
            executables.extend(self.APP_ALIASES[app_name])
        
        # Add the app name itself
        executables.append(app_name)
        
        # Try common variations
        executables.extend([
            app_name.replace(" ", "-"),
            app_name.replace(" ", "_"),
            f"gnome-{app_name}",
            f"org.gnome.{app_name.title()}",
        ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for exe in executables:
            if exe not in seen:
                seen.add(exe)
                unique.append(exe)
        
        return unique
    
    def _try_launch(self, executable: str) -> bool:
        """Try to launch an executable."""
        try:
            # Handle complex commands with arguments
            if " " in executable:
                parts = executable.split()
                cmd = parts[0]
                args = parts[1:]
            else:
                cmd = executable
                args = []
            
            # Check if command exists
            if not shutil.which(cmd) and not cmd.startswith("flatpak"):
                return False
            
            # Launch in background
            subprocess.Popen(
                [cmd] + args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            logger.info(f"Launched: {executable}")
            return True
            
        except Exception as e:
            logger.debug(f"Failed to launch {executable}: {e}")
            return False


class RunScriptTool(Tool):
    """
    Execute shell scripts or commands with safety checks.
    Allows more powerful operations than execute_command.
    """
    
    name = "run_script"
    description = "Execute a shell script or command. Can create folders, run programs, chain commands. Use for complex operations."
    parameters = [
        ToolParameter(
            name="script",
            type="string",
            description="Shell script or command to execute (e.g., 'mkdir new_folder', 'ls -la | grep py')",
            required=True
        ),
        ToolParameter(
            name="working_dir",
            type="string",
            description="Working directory for the script (default: current directory)",
            required=False
        )
    ]
    
    # Dangerous patterns that require extra confirmation (blocked for now)
    BLOCKED_PATTERNS = [
        "rm -rf /",
        "rm -rf /*",
        ":(){:|:&};:",  # Fork bomb
        "mkfs",
        "dd if=",
        "> /dev/sda",
        "chmod -R 777 /",
        "sudo rm",
        "sudo dd",
        "sudo mkfs",
    ]
    
    # Commands that are allowed
    ALLOWED_PREFIXES = [
        "ls", "cat", "head", "tail", "grep", "find", "echo", "pwd", "whoami",
        "date", "df", "du", "ps", "top", "free", "mkdir", "touch", "cp", "mv",
        "cd", "wc", "sort", "uniq", "cut", "awk", "sed",
        "python", "python3", "pip", "npm", "node", "git",
        "curl", "wget",
    ]
    
    def execute(self, script: str, working_dir: str = None) -> Dict[str, Any]:
        """Execute a shell script."""
        import os
        
        # Safety check - block dangerous patterns
        script_lower = script.lower()
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in script_lower:
                return {
                    "success": False,
                    "error": f"Blocked: Script contains dangerous pattern '{pattern}'",
                    "script": script
                }
        
        # Set working directory
        cwd = working_dir or os.getcwd()
        if not os.path.isdir(cwd):
            cwd = os.path.expanduser("~")
        
        try:
            # Execute script
            result = subprocess.run(
                script,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout.strip() or result.stderr.strip()
            
            return {
                "success": result.returncode == 0,
                "script": script,
                "output": output[:2000] if output else "Command executed successfully",
                "return_code": result.returncode,
                "working_dir": cwd
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Script timed out after 30 seconds",
                "script": script
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "script": script
            }


class CloseAppTool(Tool):
    """Close/kill an application by name."""
    
    name = "close_app"
    description = "Close or kill an application by name"
    parameters = [
        ToolParameter(
            name="app_name",
            type="string",
            description="Name of the application to close",
            required=True
        ),
        ToolParameter(
            name="force",
            type="boolean",
            description="Force kill (SIGKILL) instead of graceful close (SIGTERM)",
            required=False
        )
    ]
    
    def execute(self, app_name: str, force: bool = False) -> Dict[str, Any]:
        """Close an application."""
        import signal
        
        app_name = app_name.lower().strip()
        
        try:
            # Find processes matching the app name
            result = subprocess.run(
                ["pgrep", "-i", "-f", app_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "app": app_name,
                    "error": f"No running process found for '{app_name}'"
                }
            
            pids = result.stdout.strip().split("\n")
            
            # Kill processes
            sig = signal.SIGKILL if force else signal.SIGTERM
            killed = []
            
            for pid in pids:
                if pid:
                    try:
                        subprocess.run(["kill", f"-{sig.value}", pid], check=True)
                        killed.append(pid)
                    except:
                        pass
            
            return {
                "success": len(killed) > 0,
                "app": app_name,
                "killed_pids": killed,
                "message": f"Closed {len(killed)} instance(s) of {app_name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "app": app_name,
                "error": str(e)
            }
