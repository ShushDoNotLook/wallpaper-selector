"""DMS (DankMaterialShell) color generator implementation"""

import json
import subprocess
from pathlib import Path


class DmsColorGenerator:
    """DMS/matugen color generator backend"""

    def __init__(
        self,
        state_dir: Path,
        config_dir: Path,
        shell_dir: Path,
        session_file: Path,
    ):
        self.state_dir = state_dir
        self.config_dir = config_dir
        self.shell_dir = shell_dir
        self.session_file = session_file

    def generate(self, wallpaper_path: Path) -> bool:
        """Generate colors via DMS matugen integration"""
        try:
            subprocess.run(
                ['dms', 'matugen', 'queue',
                 '--state-dir', str(self.state_dir),
                 '--config-dir', str(self.config_dir),
                 '--shell-dir', str(self.shell_dir),
                 '--value', str(wallpaper_path)],
                check=False  # Don't fail if dms returns non-zero
            )
            return True
        except FileNotFoundError:
            print("dms command not found")
            return False
        except Exception as e:
            print(f"Error generating colors with DMS: {e}")
            return False

    def update_session(self, wallpaper_path: Path) -> bool:
        """Update DMS session.json with current wallpaper path"""
        try:
            if not self.session_file.exists():
                return False

            with open(self.session_file, 'r') as f:
                session = json.load(f)

            session['wallpaperPath'] = str(wallpaper_path)

            # Ensure parent directory exists
            self.session_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.session_file, 'w') as f:
                json.dump(session, f, indent=2)

            return True
        except Exception as e:
            print(f"Error updating DMS session: {e}")
            return False

    def get_colors_path(self) -> Path:
        """Get the path where generated colors are stored"""
        return self.state_dir / "dms-colors.json"

    def is_cached(self, wallpaper_path: Path) -> bool:
        """Check if colors are already cached for this wallpaper"""
        # Check if colors file exists
        colors_file = self.get_colors_path()
        if not colors_file.exists():
            return False

        # Check if session has the same wallpaper
        if not self.session_file.exists():
            return False

        try:
            with open(self.session_file, 'r') as f:
                session = json.load(f)
            return session.get('wallpaperPath') == str(wallpaper_path)
        except Exception:
            return False
