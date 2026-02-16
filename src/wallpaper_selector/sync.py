"""Sync current wallpaper from backend to color generator on boot"""

import time
from typing import Optional, TYPE_CHECKING

from .config import load_config
from .plugins.wallpaper import get_backend as get_wallpaper_backend
from .plugins.colors import get_backend as get_color_backend

if TYPE_CHECKING:
    from .plugins.wallpaper import WallpaperBackend
    from .plugins.colors import ColorGenerator


def wait_for_backend(backend: "WallpaperBackend", timeout: int = 10) -> bool:
    """Wait for wallpaper backend daemon to be ready"""
    for _ in range(timeout * 2):  # Check every 0.5 seconds
        try:
            wallpaper = backend.get_current_wallpaper()
            if wallpaper:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def sync_colors(wallpaper_path: str, color_generator: "ColorGenerator") -> bool:
    """Sync wallpaper to color generator"""
    try:
        # Update session file first so it initializes with correct wallpaper
        color_generator.update_session(wallpaper_path)
        # Generate colors
        color_generator.generate(wallpaper_path)
        return True
    except Exception as e:
        print(f"Error syncing colors: {e}")
        return False


def main(verbose: bool = False) -> int:
    """Main sync function - returns 0 on success, 1 on failure"""
    # Load config
    config = load_config()

    # Get wallpaper backend
    backend_class = get_wallpaper_backend(config.wallpaper.backend.name)
    if not backend_class:
        if verbose:
            print(f"sync: Unknown wallpaper backend: {config.wallpaper.backend.name}")
        return 1
    wallpaper_backend = backend_class()

    if verbose:
        print(f"sync: Waiting for {config.wallpaper.backend.name} daemon...")

    if not wait_for_backend(wallpaper_backend):
        if verbose:
            print("sync: Wallpaper backend not ready after timeout")
        return 1

    wallpaper = wallpaper_backend.get_current_wallpaper()
    if not wallpaper:
        if verbose:
            print("sync: No wallpaper found")
        return 1

    # Skip if colors disabled
    if not config.colors.enabled:
        if verbose:
            print("sync: Color generation disabled, skipping")
        return 0

    # Get color generator
    color_generator = get_color_backend(
        config.colors.backend.name,
        state_dir=config.colors.backend.state_dir,
        config_dir=config.colors.backend.config_dir,
        shell_dir=config.colors.backend.shell_dir,
        session_file=config.colors.backend.session_file,
    )

    if not color_generator:
        if verbose:
            print(f"sync: Unknown color backend: {config.colors.backend.name}")
        return 1

    if verbose:
        print(f"sync: Syncing {wallpaper} to {config.colors.backend.name}")

    if sync_colors(wallpaper, color_generator):
        if verbose:
            print("sync: Sync complete")
        return 0
    return 1
