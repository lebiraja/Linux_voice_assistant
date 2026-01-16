"""
Capabilities package - Platform detection and capability manifest.
"""

from .platform import (
    PlatformDetector,
    PlatformAdapter,
    PlatformInfo,
    AudioSystem,
    DisplayServer,
    DesktopEnvironment,
    Distribution,
    get_platform,
    get_adapter
)

from .manifest import (
    CapabilityManifest,
    Capability,
    get_manifest
)

__all__ = [
    # Platform detection
    'PlatformDetector',
    'PlatformAdapter',
    'PlatformInfo',
    'AudioSystem',
    'DisplayServer',
    'DesktopEnvironment',
    'Distribution',
    'get_platform',
    'get_adapter',
    # Capability manifest
    'CapabilityManifest',
    'Capability',
    'get_manifest',
]
