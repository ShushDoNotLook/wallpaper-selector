"""Base protocols for plugins"""

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class WallpaperBackend(Protocol):
    """Protocol for wallpaper backend implementations"""

    def is_daemon_running(self) -> bool:
        """Check if the wallpaper daemon is running"""
        ...

    def start_daemon(self) -> None:
        """Start the wallpaper daemon"""
        ...

    def get_current_wallpaper(self) -> str | None:
        """Get the path to the current wallpaper, or None if not set"""
        ...

    def set_wallpaper(self, path: Path, transition: str, duration: float, fps: int) -> bool:
        """Set the wallpaper with given transition settings"""
        ...


@runtime_checkable
class ColorGenerator(Protocol):
    """Protocol for color generator implementations"""

    def generate(self, wallpaper_path: Path) -> bool:
        """Generate colors from the given wallpaper"""
        ...

    def update_session(self, wallpaper_path: Path) -> bool:
        """Update session file with current wallpaper path"""
        ...

    def get_colors_path(self) -> Path:
        """Get the path where generated colors are stored"""
        ...
