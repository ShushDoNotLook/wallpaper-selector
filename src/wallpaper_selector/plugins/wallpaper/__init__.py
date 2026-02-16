"""Wallpaper backend plugins"""

from .base import WallpaperBackend
from .swww import SwwwBackend

# Registry of available backends
BACKENDS = {
    "swww": SwwwBackend,
}


def get_backend(name: str) -> type[WallpaperBackend] | None:
    """Get a backend class by name"""
    return BACKENDS.get(name)


__all__ = ["WallpaperBackend", "SwwwBackend", "get_backend"]
