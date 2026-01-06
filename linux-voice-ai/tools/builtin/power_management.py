
import logging
import subprocess
from typing import Dict, Any, List
from ..base import Tool, ToolParameter

logger = logging.getLogger(__name__)

class PowerManagementTool(Tool):
    """Handle system power states (shutdown, reboot, suspend)"""
    
    @property
    def name(self) -> str:
        return "power_management"
    
    @property
    def description(self) -> str:
        return (
            "Manage system power state. Can shutdown, reboot, suspend, or lock the system. "
            "CAUTION: Shutdown and reboot will verify confirmation."
        )
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="action",
                type="string",
                description="Action to perform: shutdown, reboot, suspend, logout, lock",
                required=True
            ),
            ToolParameter(
                name="confirmed",
                type="boolean",
                description="Must be set to true for destructive actions (shutdown/reboot)",
                required=False,
                default=False
            )
        ]
    
    def execute(self, action: str, confirmed: bool = False, **kwargs) -> Dict[str, Any]:
        """Execute power management command"""
        cmd = []
        
        if action in ["shutdown", "reboot"]:
            if not confirmed:
                return {
                    "success": False,
                    "error": f"Confirmation required for {action}. Please ask user for confirmation first.",
                    "requires_confirmation": True
                }
        
        if action == "shutdown":
            cmd = ["shutdown", "now"]
        elif action == "reboot":
            cmd = ["reboot"]
        elif action == "suspend":
            cmd = ["systemctl", "suspend"]
        elif action == "lock":
            # Try generic lock command first, then desktop specific
            cmd = ["xdg-screensaver", "lock"] 
        elif action == "logout":
            # This is tricky as it's DE specific. 
            # safe fallback:
            return {"success": False, "error": "Logout is desktop-environment specific and not fully supported."}
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
            
        try:
            logger.info(f"Executing power action: {action}")
            # Use sudo if needed? Usually /sbin/shutdown needs root.
            # But we can try without first or assume user has NOPASSWD sudo.
            # We'll try running it. If it fails, we'll try with sudo.
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                # Try with sudo
                cmd.insert(0, "sudo")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
            if result.returncode == 0:
                return {"success": True, "action": action, "output": result.stdout}
            else:
                return {"success": False, "error": f"Command failed: {result.stderr}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
