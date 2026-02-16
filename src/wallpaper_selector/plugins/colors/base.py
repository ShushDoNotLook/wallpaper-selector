"""Color generator protocol"""

from typing import Protocol, runtime_checkable
from pathlib import Path


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
