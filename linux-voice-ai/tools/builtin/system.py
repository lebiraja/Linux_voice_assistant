"""
System information and control tools
"""

import psutil
import subprocess
import logging
from typing import Dict, Any, List
from ..base import Tool, ToolParameter

logger = logging.getLogger(__name__)


class GetSystemInfoTool(Tool):
    """Get system information (CPU, RAM, disk)"""
    
    @property
    def name(self) -> str:
        return "get_system_info"
    
    @property
    def description(self) -> str:
        return "Get system information including CPU usage, memory usage, and disk usage."
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="info_type",
                type="string",
                description="Type of info to get: 'cpu', 'memory', 'disk', or 'all'",
                required=False,
                default="all"
            )
        ]
    
    def execute(self, info_type: str = "all", **kwargs) -> Dict[str, Any]:
        """Get system information"""
        try:
            result = {"success": True}
            
            if info_type in ["cpu", "all"]:
                result["cpu"] = {
                    "usage_percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count(),
                    "frequency_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None
                }
            
            if info_type in ["memory", "all"]:
                mem = psutil.virtual_memory()
                result["memory"] = {
                    "total_gb": round(mem.total / (1024**3), 2),
                    "available_gb": round(mem.available / (1024**3), 2),
                    "used_gb": round(mem.used / (1024**3), 2),
                    "percent": mem.percent
                }
            
            if info_type in ["disk", "all"]:
                disk = psutil.disk_usage('/')
                result["disk"] = {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent": disk.percent
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class GetProcessesTool(Tool):
    """Get list of running processes"""
    
    @property
    def name(self) -> str:
        return "get_processes"
    
    @property
    def description(self) -> str:
        return "Get list of running processes. Can filter by name pattern."
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="name_filter",
                type="string",
                description="Filter processes by name (case-insensitive substring match)",
                required=False,
                default=None
            ),
            ToolParameter(
                name="max_results",
                type="integer",
                description="Maximum number of processes to return",
                required=False,
                default=10
            )
        ]
    
    def execute(self, name_filter: str = None, max_results: int = 10, **kwargs) -> Dict[str, Any]:
        """Get running processes"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    
                    # Apply name filter
                    if name_filter and name_filter.lower() not in pinfo['name'].lower():
                        continue
                    
                    processes.append({
                        "pid": pinfo['pid'],
                        "name": pinfo['name'],
                        "cpu_percent": round(pinfo['cpu_percent'], 2),
                        "memory_percent": round(pinfo['memory_percent'], 2)
                    })
                    
                    if len(processes) >= max_results:
                        break
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                "success": True,
                "count": len(processes),
                "processes": processes
            }
            
        except Exception as e:
            logger.error(f"Error getting processes: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class ExecuteCommandTool(Tool):
    """Execute a safe shell command"""
    
    @property
    def name(self) -> str:
        return "execute_command"
    
    @property
    def description(self) -> str:
        return "Execute a safe shell command. Only allows read-only commands like ls, cat, grep, etc."
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="command",
                type="string",
                description="Command to execute (must be in safe list)",
                required=True
            )
        ]
    
    # Whitelist of safe commands
    SAFE_COMMANDS = {
        'ls', 'cat', 'grep', 'find', 'head', 'tail', 'wc', 'echo',
        'pwd', 'whoami', 'date', 'df', 'du', 'ps', 'top', 'free'
    }
    
    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute safe command"""
        try:
            # Parse command
            cmd_parts = command.split()
            if not cmd_parts:
                return {
                    "success": False,
                    "error": "Empty command"
                }
            
            # Check if command is safe
            base_cmd = cmd_parts[0]
            if base_cmd not in self.SAFE_COMMANDS:
                return {
                    "success": False,
                    "error": f"Command not allowed: {base_cmd}. Only safe read-only commands are permitted."
                }
            
            # Execute command
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                "success": result.returncode == 0,
                "command": command,
                "stdout": result.stdout[:1000],  # Limit output
                "stderr": result.stderr[:1000] if result.stderr else None,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out (5 second limit)"
            }
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {
                "success": False,
                "error": str(e)
            }
