"""Wallpaper backend protocol"""

from typing import Protocol, runtime_checkable
from pathlib import Path


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
