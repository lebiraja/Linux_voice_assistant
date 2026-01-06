
import logging
import subprocess
import re
from typing import Dict, Any, List
from ..base import Tool, ToolParameter

logger = logging.getLogger(__name__)

class SystemVolumeTool(Tool):
    """Control system master volume via ALSA (amixer)"""
    
    @property
    def name(self) -> str:
        return "control_system_volume"
    
    @property
    def description(self) -> str:
        return (
            "Control system master volume level (0-100%) and mute state. "
            "Use this for general system volume. For detailed media player control, use control_media."
        )
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="action",
                type="string",
                description="Action: set, increase, decrease, get, mute, unmute",
                required=True
            ),
            ToolParameter(
                name="value",
                type="integer",
                description="Percentage value (0-100) for set, or amount to change",
                required=False,
                default=10
            )
        ]
    
    def _run_amixer(self, args: List[str]) -> Dict[str, Any]:
        """Run amixer command"""
        try:
            cmd = ["amixer", "-D", "pulse", "set", "Master"] + args
            # Try pulse first, fallback to default if pulse missing
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                # Fallback to default
                cmd = ["amixer", "set", "Master"] + args
                result = subprocess.run(cmd, capture_output=True, text=True)
                
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_volume(self) -> Dict[str, Any]:
        """Get current volume and mute state"""
        try:
            # Use 'get' instead of 'set' for reading
            # Try pulse first
            cmd = ["amixer", "-D", "pulse", "get", "Master"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                 cmd = ["amixer", "get", "Master"]
                 result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {"success": False, "error": "Could not get volume"}

            output = result.stdout
            # Parse [50%] [on/off]
            # Example: Mono: Playback 42 [66%] [-20.00dB] [on]
            vol_match = re.search(r'\[(\d+)%\]', output)
            mute_match = re.search(r'\[(on|off)\]', output)
            
            volume = int(vol_match.group(1)) if vol_match else -1
            is_muted = (mute_match.group(1) == "off") if mute_match else False
            
            return {
                "success": True,
                "volume": volume,
                "is_muted": is_muted
            }
        except Exception as e:
             return {"success": False, "error": str(e)}

    def execute(self, action: str, value: int = 10, **kwargs) -> Dict[str, Any]:
        """Execute volume control"""
        args = []
        
        if action == "get":
            return self._get_volume()
            
        elif action == "set":
            args = [f"{value}%"]
            
        elif action == "increase":
            args = [f"{value}%+"]
            
        elif action == "decrease":
            args = [f"{value}%-"]
            
        elif action == "mute":
            args = ["mute"]
            
        elif action == "unmute":
            args = ["unmute"]
            
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
            
        result = self._run_amixer(args)
        if result["success"]:
            # Return new state
            return self._get_volume()
        else:
            return result
