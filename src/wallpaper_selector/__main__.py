"""Entry point for wallpaper-selector command"""

import os
import subprocess
import sys
from pathlib import Path

from .app import WallpaperSelector

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


def ensure_swww_daemon():
    """Ensure swww-daemon is running"""
    result = subprocess.run(['pgrep', '-x', 'swww-daemon'], capture_output=True)
    if result.returncode != 0:
        subprocess.run(['swww-daemon'], start_new_session=True)
        import time
        time.sleep(0.5)


def check_wallpaper_dir() -> bool:
    """Check if wallpaper directory has images"""
    wallpaper_dir = Path.home() / "Pictures" / "Wallpapers"
    wallpaper_dir.mkdir(parents=True, exist_ok=True)

    extensions = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'}
    for f in wallpaper_dir.iterdir():
        if f.suffix.lower() in extensions:
            return True
    return False


def main():
    """Main entry point with toggle behavior"""
    # 1. If already running, kill and exit (toggle off)
    if is_running():
        kill_existing()
        sys.exit(0)

    # 2. Setup environment
    ensure_swww_daemon()

    # 3. Check for wallpapers
    if not check_wallpaper_dir():
        subprocess.run([
            'notify-send', 'Wallpaper Selector',
            f'No wallpapers found in ~/Pictures/Wallpapers. Please add some images.'
        ])
        sys.exit(1)

    # 4. Write PID file
    PID_FILE.write_text(str(os.getpid()))

    # 5. Launch the GTK application
    app = WallpaperSelector()
    try:
        app.run(None)
    finally:
        PID_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
