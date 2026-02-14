"""Wallpaper Manager - handles wallpaper loading and state management"""

import subprocess
from pathlib import Path
from typing import List, Optional
from gi.repository import Gio


class WallpaperManager:
    """Manages wallpaper collection and current wallpaper state"""

    def __init__(self, wallpaper_dir: Path):
        self.wallpaper_dir = wallpaper_dir
        self.wallpapers: List[Path] = []
        self.current_wallpaper: Optional[str] = None
        self._load_wallpapers()
        self._get_current_wallpaper()

    def _load_wallpapers(self):
        """Load all wallpapers from directory"""
        if not self.wallpaper_dir.exists():
            self.wallpaper_dir.mkdir(parents=True, exist_ok=True)
            return

        extensions = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'}
        self.wallpapers = sorted(
            [f for f in self.wallpaper_dir.iterdir()
             if f.suffix.lower() in extensions],
            key=lambda x: x.stat().st_mtime,
            reverse=True  # newest first
        )

    def _get_current_wallpaper(self) -> Optional[str]:
        """Get current wallpaper from swww"""
        try:
            result = subprocess.run(
                ['swww', 'query'],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.split('\n'):
                if 'image:' in line:
                    self.current_wallpaper = line.split('image:')[1].strip()
                    return self.current_wallpaper
        except:
            pass
        return None

    def get_wallpapers(self) -> List[Path]:
        """Get list of wallpapers"""
        return self.wallpapers

    def get_current_wallpaper(self) -> Optional[str]:
        """Get current wallpaper path"""
        return self.current_wallpaper

    def set_wallpaper(self, path: Path) -> bool:
        """Set wallpaper using swww and regenerate colors via DMS"""
        try:
            # Set wallpaper with swww
            subprocess.run(
                ['swww', 'img', str(path), '--transition-type', 'grow',
                 '--transition-duration', '0.7', '--transition-fps', '144'],
                check=True
            )

            # Generate colors via DMS matugen integration
            subprocess.run(
                ['dms', 'matugen', 'queue',
                 '--state-dir', Path.home() / '.cache/DankMaterialShell',
                 '--config-dir', Path.home() / '.config/DankMaterialShell',
                 '--shell-dir', '/usr/share/quickshell/dms',
                 '--value', str(path)],
                check=False
            )

            # Update current wallpaper tracking
            self.current_wallpaper = str(path)
            return True
        except Exception as e:
            print(f"Error setting wallpaper: {e}")
            return False

    def refresh_current_wallpaper(self):
        """Refresh current wallpaper from system"""
        self._get_current_wallpaper()
