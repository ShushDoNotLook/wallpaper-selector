"""Sync current wallpaper from swww to DMS matugen on boot"""

import json
import subprocess
import time
from pathlib import Path
from typing import Optional

DMS_SESSION_FILE = Path.home() / ".local/state/DankMaterialShell/session.json"


def wait_for_swww(timeout: int = 10) -> bool:
    """Wait for swww-daemon to be ready"""
    for _ in range(timeout * 2):  # Check every 0.5 seconds
        try:
            result = subprocess.run(
                ['swww', 'query'],
                capture_output=True,
                check=True,
                timeout=2
            )
            if 'image:' in result.stdout.decode():
                return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
        time.sleep(0.5)
    return False


def get_current_wallpaper() -> Optional[str]:
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
                return line.split('image:')[1].strip()
    except subprocess.CalledProcessError:
        pass
    return None


def update_dms_session(wallpaper_path: str) -> bool:
    """Update DMS session.json with current wallpaper path"""
    try:
        if not DMS_SESSION_FILE.exists():
            return False

        with open(DMS_SESSION_FILE, 'r') as f:
            session = json.load(f)

        session['wallpaperPath'] = wallpaper_path

        with open(DMS_SESSION_FILE, 'w') as f:
            json.dump(session, f, indent=2)

        return True
    except Exception as e:
        print(f"Error updating DMS session: {e}")
        return False


def sync_to_dms(wallpaper_path: str) -> bool:
    """Sync wallpaper to DMS matugen"""
    try:
        # Update DMS session file first so it initializes with correct wallpaper
        update_dms_session(wallpaper_path)

        subprocess.run(
            ['dms', 'matugen', 'queue',
             '--state-dir', Path.home() / '.cache/DankMaterialShell',
             '--config-dir', Path.home() / '.config/DankMaterialShell',
             '--shell-dir', '/usr/share/quickshell/dms',
             '--value', wallpaper_path],
            check=False
        )
        return True
    except Exception as e:
        print(f"Error syncing to DMS: {e}")
        return False


def main(verbose: bool = False) -> int:
    """Main sync function - returns 0 on success, 1 on failure"""
    if verbose:
        print("wallpaper-selector-sync: Waiting for swww-daemon...")

    if not wait_for_swww():
        if verbose:
            print("wallpaper-selector-sync: swww-daemon not ready after timeout")
        return 1

    wallpaper = get_current_wallpaper()
    if not wallpaper:
        if verbose:
            print("wallpaper-selector-sync: No wallpaper found in swww")
        return 1

    if verbose:
        print(f"wallpaper-selector-sync: Syncing {wallpaper} to DMS")

    if sync_to_dms(wallpaper):
        if verbose:
            print("wallpaper-selector-sync: Sync complete")
        return 0
    return 1
