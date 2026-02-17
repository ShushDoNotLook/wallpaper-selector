"""swww wallpaper backend implementation"""

import subprocess
import time
from pathlib import Path

# Timeout for swww commands (seconds)
CMD_TIMEOUT = 5


class SwwwBackend:
    """swww wallpaper backend"""

    def is_daemon_running(self) -> bool:
        """Check if swww-daemon is running"""
        result = subprocess.run(['pgrep', '-x', 'swww-daemon'], capture_output=True, timeout=CMD_TIMEOUT)
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
                check=True,
                timeout=CMD_TIMEOUT
            )
            for line in result.stdout.split('\n'):
                if 'image:' in line:
                    return line.split('image:')[1].strip()
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
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
                check=True,
                timeout=CMD_TIMEOUT + duration  # Allow extra time for transition
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error setting wallpaper with swww: {e}")
            return False
        except subprocess.TimeoutExpired:
            print("Timeout setting wallpaper with swww")
            return False
