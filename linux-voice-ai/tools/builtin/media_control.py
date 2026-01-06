"""
Media playback control tools
Control music/video playback on Linux using MPRIS D-Bus interface
"""

import subprocess
import logging
import re
from typing import Dict, Any, List, Optional
from ..base import Tool, ToolParameter

logger = logging.getLogger(__name__)


class MediaControlTool(Tool):
    """Control media playback (play, pause, next, previous, volume, etc.)"""
    
    @property
    def name(self) -> str:
        return "control_media"
    
    @property
    def description(self) -> str:
        return (
            "Control media playback on the system. Can play, pause, stop, skip to next/previous track, "
            "adjust volume, seek, and get information about currently playing media. "
            "Works with Spotify, VLC, browsers, and most media players via MPRIS."
        )
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="action",
                type="string",
                description=(
                    "Action to perform: 'play', 'pause', 'play-pause', 'stop', 'next', 'previous', "
                    "'volume-up', 'volume-down', 'set-volume', 'mute', 'unmute', 'seek-forward', "
                    "'seek-backward', 'status', 'info'"
                ),
                required=True
            ),
            ToolParameter(
                name="value",
                type="string",
                description="Value for actions like 'set-volume' (0-100) or seek amount (seconds)",
                required=False,
                default=None
            ),
            ToolParameter(
                name="player",
                type="string",
                description="Specific player to control (spotify, vlc, firefox, etc.). If not specified, controls active player",
                required=False,
                default=None
            )
        ]
    
    def _check_playerctl_installed(self) -> bool:
        """Check if playerctl is installed"""
        try:
            result = subprocess.run(
                ["which", "playerctl"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking playerctl: {e}")
            return False
    
    def _run_playerctl(self, command: List[str], timeout: int = 5) -> Dict[str, Any]:
        """Run playerctl command and return result"""
        try:
            result = subprocess.run(
                ["playerctl"] + command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_current_status(self, player: Optional[str] = None) -> Dict[str, Any]:
        """Get current playback status"""
        cmd = []
        if player:
            cmd.extend(["-p", player])
        cmd.append("status")
        
        result = self._run_playerctl(cmd)
        if result["success"]:
            return {
                "success": True,
                "status": result["output"]
            }
        return result
    
    def _get_metadata(self, player: Optional[str] = None) -> Dict[str, Any]:
        """Get currently playing track metadata"""
        cmd = []
        if player:
            cmd.extend(["-p", player])
        cmd.extend(["metadata", "--format", "Title: {{title}}\nArtist: {{artist}}\nAlbum: {{album}}\nDuration: {{duration(position)}} / {{duration(mpris:length)}}"])
        
        result = self._run_playerctl(cmd)
        if result["success"]:
            # Parse metadata
            metadata = {}
            for line in result["output"].split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip().lower()] = value.strip()
            
            return {
                "success": True,
                "metadata": metadata,
                "raw": result["output"]
            }
        return result
    
    def _get_volume(self, player: Optional[str] = None) -> Dict[str, Any]:
        """Get current volume level"""
        cmd = []
        if player:
            cmd.extend(["-p", player])
        cmd.extend(["volume"])
        
        result = self._run_playerctl(cmd)
        if result["success"]:
            try:
                volume = float(result["output"])
                return {
                    "success": True,
                    "volume": int(volume * 100)
                }
            except ValueError:
                return {
                    "success": False,
                    "error": "Could not parse volume"
                }
        return result
    
    def _list_players(self) -> Dict[str, Any]:
        """List all available media players"""
        result = self._run_playerctl(["-l"])
        if result["success"]:
            players = [p.strip() for p in result["output"].split("\n") if p.strip()]
            return {
                "success": True,
                "players": players,
                "count": len(players)
            }
        return result
    
    def execute(
        self,
        action: str,
        value: str = None,
        player: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute media control action.
        
        Args:
            action: Action to perform (play, pause, next, previous, etc.)
            value: Optional value for certain actions
            player: Specific player to control
        """
        try:
            # Check if playerctl is installed
            if not self._check_playerctl_installed():
                return {
                    "success": False,
                    "error": "playerctl is not installed. Install with: sudo apt install playerctl"
                }
            
            action = action.lower()
            cmd = []
            
            if player:
                cmd.extend(["-p", player])
            
            # Map actions to playerctl commands
            if action == "play":
                cmd.append("play")
                result = self._run_playerctl(cmd)
                if result["success"]:
                    return {
                        "success": True,
                        "message": "Playback started",
                        "action": "play"
                    }
                return result
            
            elif action == "pause":
                cmd.append("pause")
                result = self._run_playerctl(cmd)
                if result["success"]:
                    return {
                        "success": True,
                        "message": "Playback paused",
                        "action": "pause"
                    }
                return result
            
            elif action == "play-pause":
                cmd.append("play-pause")
                result = self._run_playerctl(cmd)
                if result["success"]:
                    # Get new status
                    status = self._get_current_status(player)
                    return {
                        "success": True,
                        "message": f"Playback toggled",
                        "status": status.get("status", "unknown"),
                        "action": "play-pause"
                    }
                return result
            
            elif action == "stop":
                cmd.append("stop")
                result = self._run_playerctl(cmd)
                if result["success"]:
                    return {
                        "success": True,
                        "message": "Playback stopped",
                        "action": "stop"
                    }
                return result
            
            elif action == "next":
                cmd.append("next")
                result = self._run_playerctl(cmd)
                if result["success"]:
                    # Get new track info
                    metadata = self._get_metadata(player)
                    return {
                        "success": True,
                        "message": "Skipped to next track",
                        "action": "next",
                        "now_playing": metadata.get("metadata", {})
                    }
                return result
            
            elif action == "previous":
                cmd.append("previous")
                result = self._run_playerctl(cmd)
                if result["success"]:
                    # Get new track info
                    metadata = self._get_metadata(player)
                    return {
                        "success": True,
                        "message": "Skipped to previous track",
                        "action": "previous",
                        "now_playing": metadata.get("metadata", {})
                    }
                return result
            
            elif action == "volume-up":
                # Increase volume by 10%
                cmd.extend(["volume", "0.1+"])
                result = self._run_playerctl(cmd)
                if result["success"]:
                    vol = self._get_volume(player)
                    return {
                        "success": True,
                        "message": "Volume increased",
                        "action": "volume-up",
                        "volume": vol.get("volume", "unknown")
                    }
                return result
            
            elif action == "volume-down":
                # Decrease volume by 10%
                cmd.extend(["volume", "0.1-"])
                result = self._run_playerctl(cmd)
                if result["success"]:
                    vol = self._get_volume(player)
                    return {
                        "success": True,
                        "message": "Volume decreased",
                        "action": "volume-down",
                        "volume": vol.get("volume", "unknown")
                    }
                return result
            
            elif action == "set-volume":
                if not value:
                    return {
                        "success": False,
                        "error": "Volume value required (0-100)"
                    }
                try:
                    vol_percent = int(value)
                    if not 0 <= vol_percent <= 100:
                        raise ValueError("Volume must be between 0-100")
                    
                    vol_decimal = vol_percent / 100.0
                    cmd.extend(["volume", str(vol_decimal)])
                    result = self._run_playerctl(cmd)
                    if result["success"]:
                        return {
                            "success": True,
                            "message": f"Volume set to {vol_percent}%",
                            "action": "set-volume",
                            "volume": vol_percent
                        }
                    return result
                except ValueError as e:
                    return {
                        "success": False,
                        "error": f"Invalid volume value: {e}"
                    }
            
            elif action == "mute":
                cmd.extend(["volume", "0"])
                result = self._run_playerctl(cmd)
                if result["success"]:
                    return {
                        "success": True,
                        "message": "Muted",
                        "action": "mute"
                    }
                return result
            
            elif action == "unmute":
                cmd.extend(["volume", "0.5"])
                result = self._run_playerctl(cmd)
                if result["success"]:
                    return {
                        "success": True,
                        "message": "Unmuted to 50%",
                        "action": "unmute",
                        "volume": 50
                    }
                return result
            
            elif action == "seek-forward":
                # Seek forward 10 seconds by default
                seek_amount = value if value else "10"
                cmd.extend(["position", f"{seek_amount}+"])
                result = self._run_playerctl(cmd)
                if result["success"]:
                    return {
                        "success": True,
                        "message": f"Seeked forward {seek_amount} seconds",
                        "action": "seek-forward"
                    }
                return result
            
            elif action == "seek-backward":
                # Seek backward 10 seconds by default
                seek_amount = value if value else "10"
                cmd.extend(["position", f"{seek_amount}-"])
                result = self._run_playerctl(cmd)
                if result["success"]:
                    return {
                        "success": True,
                        "message": f"Seeked backward {seek_amount} seconds",
                        "action": "seek-backward"
                    }
                return result
            
            elif action == "status":
                status = self._get_current_status(player)
                if status["success"]:
                    players = self._list_players()
                    return {
                        "success": True,
                        "status": status["status"],
                        "available_players": players.get("players", []),
                        "action": "status"
                    }
                return status
            
            elif action == "info":
                metadata = self._get_metadata(player)
                if metadata["success"]:
                    status = self._get_current_status(player)
                    volume = self._get_volume(player)
                    
                    return {
                        "success": True,
                        "metadata": metadata.get("metadata", {}),
                        "status": status.get("status", "unknown"),
                        "volume": volume.get("volume", "unknown"),
                        "action": "info"
                    }
                return metadata
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}. Valid actions: play, pause, play-pause, stop, next, previous, volume-up, volume-down, set-volume, mute, unmute, seek-forward, seek-backward, status, info"
                }
            
        except Exception as e:
            logger.error(f"Error in media control: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class GetNowPlayingTool(Tool):
    """Get information about currently playing media"""
    
    @property
    def name(self) -> str:
        return "get_now_playing"
    
    @property
    def description(self) -> str:
        return "Get information about the currently playing track/media (title, artist, album, etc.)"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="player",
                type="string",
                description="Specific player to query (optional)",
                required=False,
                default=None
            )
        ]
    
    def execute(self, player: str = None, **kwargs) -> Dict[str, Any]:
        """Get now playing info"""
        media_tool = MediaControlTool()
        return media_tool.execute(action="info", player=player)
