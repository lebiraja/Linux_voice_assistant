"""
Platform detection and compatibility layer.
Handles differences between Ubuntu/Arch, X11/Wayland, PulseAudio/PipeWire.
"""

import os
import subprocess
import shutil
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum

logger = logging.getLogger(__name__)


class AudioSystem(Enum):
    PIPEWIRE = "pipewire"
    PULSEAUDIO = "pulseaudio"
    ALSA = "alsa"
    UNKNOWN = "unknown"


class DisplayServer(Enum):
    WAYLAND = "wayland"
    X11 = "x11"
    XWAYLAND = "xwayland"  # Wayland with X11 compat
    HEADLESS = "headless"


class DesktopEnvironment(Enum):
    GNOME = "gnome"
    KDE = "kde"
    XFCE = "xfce"
    SWAY = "sway"
    I3 = "i3"
    HYPRLAND = "hyprland"
    CINNAMON = "cinnamon"
    MATE = "mate"
    UNKNOWN = "unknown"


class Distribution(Enum):
    UBUNTU = "ubuntu"
    DEBIAN = "debian"
    ARCH = "arch"
    MANJARO = "manjaro"
    FEDORA = "fedora"
    OPENSUSE = "opensuse"
    NIXOS = "nixos"
    UNKNOWN = "unknown"


@dataclass
class PlatformInfo:
    """Complete platform information"""
    distribution: Distribution
    audio_system: AudioSystem
    display_server: DisplayServer
    desktop_environment: DesktopEnvironment
    has_systemd: bool
    has_playerctl: bool
    has_amixer: bool
    uid: int
    audio_socket: Optional[str]
    display: Optional[str]
    wayland_display: Optional[str]
    xdg_runtime_dir: Optional[str]


class PlatformDetector:
    """Detect and adapt to different Linux platforms"""

    _cached_info: Optional[PlatformInfo] = None

    @classmethod
    def detect(cls) -> PlatformInfo:
        """Detect full platform information (cached)"""
        if cls._cached_info is None:
            cls._cached_info = cls._do_detect()
            cls._log_platform_info(cls._cached_info)
        return cls._cached_info

    @classmethod
    def _do_detect(cls) -> PlatformInfo:
        """Perform actual detection"""
        uid = os.getuid()
        xdg_runtime = os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{uid}')

        audio_system = cls._detect_audio_system(xdg_runtime)
        display_server = cls._detect_display_server()

        return PlatformInfo(
            distribution=cls._detect_distribution(),
            audio_system=audio_system,
            display_server=display_server,
            desktop_environment=cls._detect_desktop_environment(),
            has_systemd=cls._check_command('systemctl'),
            has_playerctl=cls._check_command('playerctl'),
            has_amixer=cls._check_command('amixer'),
            uid=uid,
            audio_socket=cls._get_audio_socket(audio_system, xdg_runtime),
            display=os.environ.get('DISPLAY'),
            wayland_display=os.environ.get('WAYLAND_DISPLAY'),
            xdg_runtime_dir=xdg_runtime
        )

    @staticmethod
    def _detect_audio_system(xdg_runtime: str) -> AudioSystem:
        """Detect which audio system is in use"""
        # Check for PipeWire
        pipewire_socket = Path(f"{xdg_runtime}/pipewire-0")
        if pipewire_socket.exists():
            return AudioSystem.PIPEWIRE

        # Check if pipewire process is running
        try:
            result = subprocess.run(
                ['pgrep', '-x', 'pipewire'],
                capture_output=True, timeout=2
            )
            if result.returncode == 0:
                return AudioSystem.PIPEWIRE
        except Exception:
            pass

        # Check for PulseAudio
        pulse_socket = Path(f"{xdg_runtime}/pulse/native")
        if pulse_socket.exists():
            return AudioSystem.PULSEAUDIO

        # Check if pulseaudio process is running
        try:
            result = subprocess.run(
                ['pgrep', '-x', 'pulseaudio'],
                capture_output=True, timeout=2
            )
            if result.returncode == 0:
                return AudioSystem.PULSEAUDIO
        except Exception:
            pass

        # Fallback to ALSA if amixer exists
        if shutil.which('amixer'):
            return AudioSystem.ALSA

        return AudioSystem.UNKNOWN

    @staticmethod
    def _detect_display_server() -> DisplayServer:
        """Detect display server (X11, Wayland, XWayland)"""
        wayland_display = os.environ.get('WAYLAND_DISPLAY')
        x11_display = os.environ.get('DISPLAY')

        if wayland_display:
            # Wayland session
            if x11_display and Path('/tmp/.X11-unix').exists():
                # XWayland is also available
                return DisplayServer.XWAYLAND
            return DisplayServer.WAYLAND

        if x11_display:
            return DisplayServer.X11

        return DisplayServer.HEADLESS

    @staticmethod
    def _detect_desktop_environment() -> DesktopEnvironment:
        """Detect desktop environment"""
        # Check XDG_CURRENT_DESKTOP first
        xdg_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        session_desktop = os.environ.get('XDG_SESSION_DESKTOP', '').lower()
        desktop_session = os.environ.get('DESKTOP_SESSION', '').lower()

        combined = f"{xdg_desktop} {session_desktop} {desktop_session}"

        if 'gnome' in combined:
            return DesktopEnvironment.GNOME
        if 'kde' in combined or 'plasma' in combined:
            return DesktopEnvironment.KDE
        if 'xfce' in combined:
            return DesktopEnvironment.XFCE
        if 'sway' in combined:
            return DesktopEnvironment.SWAY
        if 'i3' in combined:
            return DesktopEnvironment.I3
        if 'hyprland' in combined:
            return DesktopEnvironment.HYPRLAND
        if 'cinnamon' in combined:
            return DesktopEnvironment.CINNAMON
        if 'mate' in combined:
            return DesktopEnvironment.MATE

        return DesktopEnvironment.UNKNOWN

    @staticmethod
    def _detect_distribution() -> Distribution:
        """Detect Linux distribution"""
        os_release = Path('/etc/os-release')

        if os_release.exists():
            content = os_release.read_text().lower()

            if 'ubuntu' in content:
                return Distribution.UBUNTU
            if 'debian' in content:
                return Distribution.DEBIAN
            if 'arch' in content:
                return Distribution.ARCH
            if 'manjaro' in content:
                return Distribution.MANJARO
            if 'fedora' in content:
                return Distribution.FEDORA
            if 'opensuse' in content or 'suse' in content:
                return Distribution.OPENSUSE
            if 'nixos' in content:
                return Distribution.NIXOS

        return Distribution.UNKNOWN

    @staticmethod
    def _check_command(command: str) -> bool:
        """Check if a command is available"""
        return shutil.which(command) is not None

    @staticmethod
    def _get_audio_socket(audio_system: AudioSystem, xdg_runtime: str) -> Optional[str]:
        """Get the appropriate audio socket path"""
        if audio_system == AudioSystem.PIPEWIRE:
            # PipeWire provides PulseAudio compatibility socket
            pulse_compat = f"{xdg_runtime}/pulse/native"
            if Path(pulse_compat).exists():
                return pulse_compat
            return f"{xdg_runtime}/pipewire-0"

        if audio_system == AudioSystem.PULSEAUDIO:
            return f"{xdg_runtime}/pulse/native"

        return None

    @staticmethod
    def _log_platform_info(info: PlatformInfo):
        """Log detected platform information"""
        logger.info(f"Platform Detection Results:")
        logger.info(f"  Distribution: {info.distribution.value}")
        logger.info(f"  Audio: {info.audio_system.value}")
        logger.info(f"  Display: {info.display_server.value}")
        logger.info(f"  Desktop: {info.desktop_environment.value}")
        logger.info(f"  systemd: {info.has_systemd}")
        logger.info(f"  playerctl: {info.has_playerctl}")
        logger.info(f"  Audio Socket: {info.audio_socket}")


class PlatformAdapter:
    """Provide platform-specific implementations"""

    def __init__(self):
        self.platform = PlatformDetector.detect()

    def get_volume_command(self, action: str, value: int = None) -> List[str]:
        """Get volume control command for this platform"""
        if self.platform.audio_system == AudioSystem.PIPEWIRE:
            # Use wpctl for PipeWire
            if shutil.which('wpctl'):
                if action == 'get':
                    return ['wpctl', 'get-volume', '@DEFAULT_AUDIO_SINK@']
                elif action == 'set':
                    return ['wpctl', 'set-volume', '@DEFAULT_AUDIO_SINK@', f'{value}%']
                elif action == 'mute':
                    return ['wpctl', 'set-mute', '@DEFAULT_AUDIO_SINK@', 'toggle']

        # Fallback to amixer (works with both PulseAudio and ALSA)
        if action == 'get':
            return ['amixer', 'get', 'Master']
        elif action == 'set':
            return ['amixer', 'set', 'Master', f'{value}%']
        elif action == 'mute':
            return ['amixer', 'set', 'Master', 'toggle']

        return []

    def get_lock_screen_command(self) -> List[str]:
        """Get screen lock command for this platform"""
        de = self.platform.desktop_environment
        ds = self.platform.display_server

        # Wayland compositors
        if ds in (DisplayServer.WAYLAND, DisplayServer.XWAYLAND):
            if de == DesktopEnvironment.SWAY and shutil.which('swaylock'):
                return ['swaylock']
            if de == DesktopEnvironment.HYPRLAND and shutil.which('hyprlock'):
                return ['hyprlock']
            if de == DesktopEnvironment.GNOME:
                return ['loginctl', 'lock-session']
            if de == DesktopEnvironment.KDE:
                return ['loginctl', 'lock-session']

        # X11 fallbacks
        if shutil.which('xdg-screensaver'):
            return ['xdg-screensaver', 'lock']
        if shutil.which('i3lock'):
            return ['i3lock']

        # Generic systemd
        if self.platform.has_systemd:
            return ['loginctl', 'lock-session']

        return []

    def get_brightness_interface(self) -> Optional[str]:
        """Get brightness control interface"""
        backlight_dir = Path('/sys/class/backlight')

        if not backlight_dir.exists():
            return None

        # Prefer intel_backlight, then amdgpu_bl, then any
        preferred = ['intel_backlight', 'amdgpu_bl0', 'acpi_video0']

        for device in preferred:
            if (backlight_dir / device).exists():
                return str(backlight_dir / device)

        # Use first available
        devices = list(backlight_dir.iterdir())
        if devices:
            return str(devices[0])

        return None

    def get_terminal_command(self) -> str:
        """Get the best terminal emulator for this platform"""
        de = self.platform.desktop_environment

        # DE-specific terminals first
        de_terminals = {
            DesktopEnvironment.GNOME: ['gnome-terminal', 'kgx'],
            DesktopEnvironment.KDE: ['konsole', 'yakuake'],
            DesktopEnvironment.XFCE: ['xfce4-terminal'],
            DesktopEnvironment.SWAY: ['alacritty', 'foot', 'kitty'],
            DesktopEnvironment.HYPRLAND: ['kitty', 'alacritty', 'foot'],
            DesktopEnvironment.I3: ['alacritty', 'urxvt', 'xterm'],
        }

        preferred = de_terminals.get(de, [])

        # Generic fallback list
        fallbacks = ['alacritty', 'kitty', 'gnome-terminal', 'konsole',
                     'xfce4-terminal', 'terminator', 'xterm']

        for terminal in preferred + fallbacks:
            if shutil.which(terminal):
                return terminal

        return 'xterm'  # Last resort

    def get_file_manager_command(self) -> str:
        """Get the best file manager for this platform"""
        de = self.platform.desktop_environment

        de_managers = {
            DesktopEnvironment.GNOME: ['nautilus', 'org.gnome.Nautilus'],
            DesktopEnvironment.KDE: ['dolphin'],
            DesktopEnvironment.XFCE: ['thunar'],
            DesktopEnvironment.CINNAMON: ['nemo'],
            DesktopEnvironment.MATE: ['caja'],
        }

        preferred = de_managers.get(de, [])
        fallbacks = ['nautilus', 'dolphin', 'thunar', 'nemo', 'pcmanfm', 'ranger']

        for fm in preferred + fallbacks:
            if shutil.which(fm):
                return fm

        return 'xdg-open'  # Fallback

    def can_use_global_hotkeys(self) -> bool:
        """Check if global hotkeys are supported"""
        ds = self.platform.display_server

        if ds == DisplayServer.X11:
            return True

        if ds == DisplayServer.XWAYLAND:
            # XWayland provides X11 compatibility
            return True

        if ds == DisplayServer.WAYLAND:
            # Pure Wayland - need special handling
            # TODO: Check for evdev access or portal support
            return False

        return False

    def get_hotkey_backend(self) -> str:
        """Get the recommended hotkey backend"""
        ds = self.platform.display_server

        if ds in (DisplayServer.X11, DisplayServer.XWAYLAND):
            return 'pynput'  # Works with X11

        if ds == DisplayServer.WAYLAND:
            # Check for evdev access
            if Path('/dev/input').exists():
                return 'evdev'
            return 'none'

        return 'none'

    def get_docker_audio_mounts(self) -> Dict[str, str]:
        """Get Docker volume mounts for audio"""
        mounts = {}

        if self.platform.audio_socket:
            socket_path = self.platform.audio_socket
            mounts[socket_path] = f"{socket_path}:ro"

        # Also mount pipewire socket if available
        xdg = self.platform.xdg_runtime_dir
        pipewire = f"{xdg}/pipewire-0"
        if Path(pipewire).exists() and pipewire not in mounts:
            mounts[pipewire] = f"{pipewire}:ro"

        return mounts

    def get_docker_display_mounts(self) -> Dict[str, str]:
        """Get Docker volume mounts for display"""
        mounts = {}
        ds = self.platform.display_server

        if ds in (DisplayServer.X11, DisplayServer.XWAYLAND):
            mounts['/tmp/.X11-unix'] = '/tmp/.X11-unix:rw'

        if ds in (DisplayServer.WAYLAND, DisplayServer.XWAYLAND):
            xdg = self.platform.xdg_runtime_dir
            wayland = self.platform.wayland_display
            if wayland:
                mounts[f"{xdg}/{wayland}"] = f"{xdg}/{wayland}:ro"

        return mounts

    def get_docker_environment(self) -> Dict[str, str]:
        """Get Docker environment variables"""
        env = {}

        if self.platform.display:
            env['DISPLAY'] = self.platform.display

        if self.platform.wayland_display:
            env['WAYLAND_DISPLAY'] = self.platform.wayland_display

        if self.platform.xdg_runtime_dir:
            env['XDG_RUNTIME_DIR'] = self.platform.xdg_runtime_dir

        if self.platform.audio_socket:
            env['PULSE_SERVER'] = f"unix:{self.platform.audio_socket}"

        return env


# Convenience function
def get_platform() -> PlatformInfo:
    """Get platform information"""
    return PlatformDetector.detect()


def get_adapter() -> PlatformAdapter:
    """Get platform adapter"""
    return PlatformAdapter()
