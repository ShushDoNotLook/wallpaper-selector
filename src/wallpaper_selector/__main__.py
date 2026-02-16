"""Entry point for wallpaper-selector command"""

import os
import subprocess
import sys
from pathlib import Path

from .app import WallpaperSelector
from .config import load_config
from .plugins.wallpaper import get_backend as get_wallpaper_backend
from .plugins.colors import get_backend as get_color_backend
from .sync import main as sync_main

PID_FILE = Path("/tmp/wallpaper-selector.pid")


def is_running() -> bool:
    """Check if wallpaper selector is already running via PID file"""
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            # Check if process is still running
            os.kill(pid, 0)  # Raises OSError if process doesn't exist
            return True
        except (ValueError, OSError):
            PID_FILE.unlink(missing_ok=True)
    return False


def kill_existing():
    """Kill any existing wallpaper selector instances"""
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, 15)  # SIGTERM
        except (ValueError, OSError):
            pass
        PID_FILE.unlink(missing_ok=True)


def check_wallpaper_dir(config) -> bool:
    """Check if wallpaper directory has images"""
    wallpaper_dir = config.wallpaper.directory
    wallpaper_dir.mkdir(parents=True, exist_ok=True)

    extensions = {f".{ext.lower()}" if not ext.startswith(".") else ext.lower()
                  for ext in config.wallpaper.extensions}
    for f in wallpaper_dir.iterdir():
        if f.suffix.lower() in extensions:
            return True
    return False


def main():
    """Main entry point with CLI support"""
    # Check for sync mode
    if len(sys.argv) > 1 and sys.argv[1] == 'sync':
        verbose = '--verbose' in sys.argv or '-v' in sys.argv
        sys.exit(sync_main(verbose=verbose))

    # Load config
    config = load_config()

    # Get wallpaper backend
    backend_class = get_wallpaper_backend(config.wallpaper.backend.name)
    if not backend_class:
        print(f"Unknown wallpaper backend: {config.wallpaper.backend.name}")
        sys.exit(1)
    wallpaper_backend = backend_class()

    # GUI mode: toggle behavior
    # 1. If already running, kill and exit (toggle off)
    if is_running():
        kill_existing()
        sys.exit(0)

    # 2. Setup environment - ensure daemon is running
    if not wallpaper_backend.is_daemon_running():
        wallpaper_backend.start_daemon()

    # 3. Check for wallpapers
    if not check_wallpaper_dir(config):
        subprocess.run([
            'notify-send', 'Wallpaper Selector',
            f'No wallpapers found in {config.wallpaper.directory}. Please add some images.'
        ])
        sys.exit(1)

    # 4. Write PID file
    PID_FILE.write_text(str(os.getpid()))

    # 5. Get color generator if enabled
    color_generator = None
    if config.colors.enabled:
        color_generator = get_color_backend(
            config.colors.backend.name,
            state_dir=config.colors.backend.state_dir,
            config_dir=config.colors.backend.config_dir,
            shell_dir=config.colors.backend.shell_dir,
            session_file=config.colors.backend.session_file,
        )

    # 6. Launch the GTK application
    app = WallpaperSelector(config, wallpaper_backend, color_generator)
    try:
        app.run(None)
    finally:
        PID_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
