"""Base View - common functionality for all views"""

from pathlib import Path
from typing import Optional, TYPE_CHECKING
from gi.repository import Gtk, Gio

if TYPE_CHECKING:
    from wallpaper_selector.models.wallpaper_manager import WallpaperManager


class BaseView:
    """Base class for all views with common functionality"""

    def __init__(self, wallpaper_manager: 'WallpaperManager'):
        self.wallpaper_manager = wallpaper_manager
        self.widget: Optional[Gtk.Widget] = None

    def build(self) -> Gtk.Widget:
        """Build and return the main widget for this view"""
        raise NotImplementedError

    def update(self):
        """Update view content/refresh data"""
        raise NotImplementedError

    def set_current_wallpaper_indicator(self, path: Path, is_current: bool):
        """Update visual indicator for current wallpaper"""
        pass

    def cleanup(self):
        """Clean up resources when view is destroyed"""
        pass
