"""Wallpaper Manager - handles wallpaper loading and state management"""

from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

from ..cache import cache_wallpaper
from ..config import Config

if TYPE_CHECKING:
    from ..plugins.wallpaper import WallpaperBackend
    from ..plugins.colors import ColorGenerator


class WallpaperManager:
    """Manages wallpaper collection and current wallpaper state"""

    def __init__(
        self,
        config: Config,
        wallpaper_backend: "WallpaperBackend",
        color_generator: Optional["ColorGenerator"] = None,
    ):
        self.config = config
        self.wallpaper_backend = wallpaper_backend
        self.color_generator = color_generator
        self.wallpapers: List[Path] = []
        self.current_wallpaper: Optional[str] = None
        self._load_wallpapers()
        self._get_current_wallpaper()

    def _load_wallpapers(self):
        """Load all wallpapers from directory"""
        wallpaper_dir = self.config.wallpaper.directory
        if not wallpaper_dir.exists():
            wallpaper_dir.mkdir(parents=True, exist_ok=True)
            return

        # Get extensions with leading dot
        extensions = {f".{ext.lower()}" if not ext.startswith(".") else ext.lower()
                      for ext in self.config.wallpaper.extensions}

        self.wallpapers = sorted(
            [f for f in wallpaper_dir.iterdir()
             if f.suffix.lower() in extensions],
            key=lambda x: x.stat().st_mtime,
            reverse=True  # newest first
        )

    def _get_current_wallpaper(self) -> Optional[str]:
        """Get current wallpaper from backend"""
        self.current_wallpaper = self.wallpaper_backend.get_current_wallpaper()
        return self.current_wallpaper

    @property
    def wallpaper_dir(self) -> Path:
        """Get wallpaper directory"""
        return self.config.wallpaper.directory

    def get_wallpapers(self) -> List[Path]:
        """Get list of wallpapers"""
        return self.wallpapers

    def get_current_wallpaper(self) -> Optional[str]:
        """Get current wallpaper path"""
        return self.current_wallpaper

    def set_wallpaper(self, path: Path) -> bool:
        """Set wallpaper using backend and optionally regenerate colors"""
        backend_config = self.config.wallpaper.backend

        # Set wallpaper with backend
        if not self.wallpaper_backend.set_wallpaper(
            path,
            backend_config.transition_type,
            backend_config.transition_duration,
            backend_config.transition_fps,
        ):
            return False

        # Cache wallpaper for fast boot sync
        cache_wallpaper(path)

        # Generate colors if enabled and generator available
        if self.config.colors.enabled and self.color_generator:
            self.color_generator.generate(path)

        # Update current wallpaper tracking
        self.current_wallpaper = str(path)
        return True

    def refresh_current_wallpaper(self):
        """Refresh current wallpaper from system"""
        self._get_current_wallpaper()
