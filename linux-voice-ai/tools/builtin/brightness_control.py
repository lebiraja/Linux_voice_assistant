
import logging
import os
from typing import Dict, Any, List
from ..base import Tool, ToolParameter

logger = logging.getLogger(__name__)

class BrightnessControlTool(Tool):
    """Control screen brightness via /sys/class/backlight"""
    
    @property
    def name(self) -> str:
        return "control_brightness"
    
    @property
    def description(self) -> str:
        return (
            "Control screen brightness level (0-100%). "
            "Can set specific percentage or adjust relatively."
        )
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="action",
                type="string",
                description="Action to perform: set, increase, decrease, get",
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
    
    def _find_backlight_device(self):
        """Find the first available backlight device"""
        base_path = "/sys/class/backlight"
        if not os.path.exists(base_path):
            return None
            
        devices = os.listdir(base_path)
        if not devices:
            return None
            
        # Prefer intel_backlight if available
        if "intel_backlight" in devices:
            return os.path.join(base_path, "intel_backlight")
        return os.path.join(base_path, devices[0])

    def execute(self, action: str, value: int = 10, **kwargs) -> Dict[str, Any]:
        """Execute brightness control"""
        device_path = self._find_backlight_device()
        if not device_path:
            return {
                "success": False,
                "error": "No backlight device found. This feature works on laptops/integrated displays."
            }
            
        try:
            max_path = os.path.join(device_path, "max_brightness")
            curr_path = os.path.join(device_path, "brightness")
            
            with open(max_path, 'r') as f:
                max_val = int(f.read().strip())
                
            with open(curr_path, 'r') as f:
                curr_val = int(f.read().strip())
                
            curr_percent = int((curr_val / max_val) * 100)
            new_val = curr_val
            
            if action == "get":
                return {
                    "success": True,
                    "brightness": curr_percent
                }
                
            elif action == "set":
                if value < 0 or value > 100:
                    return {"success": False, "error": "Value must be between 0 and 100"}
                new_val = int((value / 100) * max_val)
                
            elif action == "increase":
                new_percent = min(100, curr_percent + value)
                new_val = int((new_percent / 100) * max_val)
                
            elif action == "decrease":
                new_percent = max(0, curr_percent - value)
                new_val = int((new_percent / 100) * max_val)
                
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
            # Write new value
            try:
                with open(curr_path, 'w') as f:
                    f.write(str(new_val))
            except PermissionError:
                # Try with tee if direct write fails (unlikely in container but possible)
                return {
                    "success": False,
                    "error": "Permission denied. Need udev rules or root access to write to brightness file."
                }
                
            return {
                "success": True, 
                "brightness": int((new_val / max_val) * 100),
                "action": action
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
