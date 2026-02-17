"""Sync current wallpaper from cache to color generator on boot"""

from typing import TYPE_CHECKING

from .cache import get_cached_wallpaper
from .config import load_config
from .plugins.colors import get_backend as get_color_backend

if TYPE_CHECKING:
    from .plugins.colors import ColorGenerator


def sync_colors(wallpaper_path: str, color_generator: "ColorGenerator", verbose: bool = False) -> bool:
    """Sync wallpaper to color generator"""
    try:
        # Check if colors are already cached for this wallpaper
        if color_generator.is_cached(wallpaper_path):
            if verbose:
                print("sync: Colors already cached, updating session only")
            # Still update session to ensure DMS knows current wallpaper
            color_generator.update_session(wallpaper_path)
            return True

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

    # Get cached wallpaper (fast, no waiting for swww)
    wallpaper = get_cached_wallpaper()
    if not wallpaper:
        if verbose:
            print("sync: No cached wallpaper found")
        return 1

    if verbose:
        print(f"sync: Found cached wallpaper: {wallpaper}")

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
        print(f"sync: Syncing to {config.colors.backend.name}")

    if sync_colors(wallpaper, color_generator, verbose=verbose):
        if verbose:
            print("sync: Complete")
        return 0
    return 1
