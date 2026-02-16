"""swww wallpaper backend implementation"""

import subprocess
import time
from pathlib import Path


class SwwwBackend:
    """swww wallpaper backend"""

    def is_daemon_running(self) -> bool:
        """Check if swww-daemon is running"""
        result = subprocess.run(['pgrep', '-x', 'swww-daemon'], capture_output=True)
        return result.returncode == 0

    def start_daemon(self) -> None:
        """Start swww-daemon"""
        subprocess.run(['swww-daemon'], start_new_session=True)
        # Wait for daemon to initialize
        time.sleep(0.5)

    def get_current_wallpaper(self) -> str | None:
        """Get current wallpaper from swww query"""
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
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return None

    def set_wallpaper(self, path: Path, transition: str, duration: float, fps: int) -> bool:
        """Set wallpaper using swww"""
        try:
            subprocess.run(
                ['swww', 'img', str(path),
                 '--transition-type', transition,
                 '--transition-duration', str(duration),
                 '--transition-fps', str(fps)],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error setting wallpaper with swww: {e}")
            return False
