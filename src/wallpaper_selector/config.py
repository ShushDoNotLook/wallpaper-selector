"""Configuration loading and management"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


CONFIG_DIR = Path.home() / ".config" / "wallpaper-selector"
CONFIG_FILE = CONFIG_DIR / "config.toml"


def expand_path(path: str) -> Path:
    """Expand ~ in path strings"""
    return Path(path).expanduser()


@dataclass
class WallpaperBackendConfig:
    """Wallpaper backend configuration"""
    name: str = "swww"
    transition_type: str = "grow"
    transition_duration: float = 0.7
    transition_fps: int = 144


@dataclass
class WallpaperConfig:
    """Wallpaper settings"""
    directory: Path = field(default_factory=lambda: Path.home() / "Pictures" / "Wallpapers")
    extensions: List[str] = field(default_factory=lambda: ["png", "jpg", "jpeg", "webp", "gif", "bmp"])
    backend: WallpaperBackendConfig = field(default_factory=WallpaperBackendConfig)


@dataclass
class ColorsBackendConfig:
    """Color generator backend configuration"""
    name: str = "dms"
    state_dir: Path = field(default_factory=lambda: Path.home() / ".cache" / "DankMaterialShell")
    config_dir: Path = field(default_factory=lambda: Path.home() / ".config" / "DankMaterialShell")
    shell_dir: Path = field(default_factory=lambda: Path("/usr/share/quickshell/dms"))
    session_file: Path = field(default_factory=lambda: Path.home() / ".local" / "state" / "DankMaterialShell" / "session.json")


@dataclass
class ColorsConfig:
    """Color generation settings"""
    enabled: bool = True
    backend: ColorsBackendConfig = field(default_factory=ColorsBackendConfig)


@dataclass
class UIConfig:
    """UI settings"""
    window_width: int = 1100
    window_height: int = 550


@dataclass
class Config:
    """Main configuration"""
    wallpaper: WallpaperConfig = field(default_factory=WallpaperConfig)
    colors: ColorsConfig = field(default_factory=ColorsConfig)
    ui: UIConfig = field(default_factory=UIConfig)


def _parse_wallpaper_backend(data: dict) -> WallpaperBackendConfig:
    """Parse wallpaper backend config from TOML dict"""
    return WallpaperBackendConfig(
        name=data.get("name", "swww"),
        transition_type=data.get("transition_type", "grow"),
        transition_duration=data.get("transition_duration", 0.7),
        transition_fps=data.get("transition_fps", 144),
    )


def _parse_wallpaper(data: dict) -> WallpaperConfig:
    """Parse wallpaper config from TOML dict"""
    backend_data = data.get("backend", {})
    return WallpaperConfig(
        directory=expand_path(data.get("directory", "~/Pictures/Wallpapers")),
        extensions=data.get("extensions", ["png", "jpg", "jpeg", "webp", "gif", "bmp"]),
        backend=_parse_wallpaper_backend(backend_data),
    )


def _parse_colors_backend(data: dict) -> ColorsBackendConfig:
    """Parse colors backend config from TOML dict"""
    return ColorsBackendConfig(
        name=data.get("name", "dms"),
        state_dir=expand_path(data.get("state_dir", "~/.cache/DankMaterialShell")),
        config_dir=expand_path(data.get("config_dir", "~/.config/DankMaterialShell")),
        shell_dir=Path(data.get("shell_dir", "/usr/share/quickshell/dms")),
        session_file=expand_path(data.get("session_file", "~/.local/state/DankMaterialShell/session.json")),
    )


def _parse_colors(data: dict) -> ColorsConfig:
    """Parse colors config from TOML dict"""
    backend_data = data.get("backend", {})
    return ColorsConfig(
        enabled=data.get("enabled", True),
        backend=_parse_colors_backend(backend_data),
    )


def _parse_ui(data: dict) -> UIConfig:
    """Parse UI config from TOML dict"""
    return UIConfig(
        window_width=data.get("window_width", 1100),
        window_height=data.get("window_height", 550),
    )


def load_config() -> Config:
    """Load configuration from file, creating default if not exists"""
    if not CONFIG_FILE.exists():
        config = Config()
        save_config(config)
        return config

    try:
        with open(CONFIG_FILE, "rb") as f:
            data = tomllib.load(f)

        return Config(
            wallpaper=_parse_wallpaper(data.get("wallpaper", {})),
            colors=_parse_colors(data.get("colors", {})),
            ui=_parse_ui(data.get("ui", {})),
        )
    except Exception as e:
        print(f"Error loading config: {e}, using defaults")
        return Config()


def save_config(config: Config) -> None:
    """Save configuration to file (creates default config)"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    content = f'''# Wallpaper Selector Configuration

[wallpaper]
directory = "{config.wallpaper.directory}"
extensions = {config.wallpaper.extensions}

[wallpaper.backend]
name = "{config.wallpaper.backend.name}"
transition_type = "{config.wallpaper.backend.transition_type}"
transition_duration = {config.wallpaper.backend.transition_duration}
transition_fps = {config.wallpaper.backend.transition_fps}

[colors]
enabled = {str(config.colors.enabled).lower()}

[colors.backend]
name = "{config.colors.backend.name}"
state_dir = "{config.colors.backend.state_dir}"
config_dir = "{config.colors.backend.config_dir}"
shell_dir = "{config.colors.backend.shell_dir}"
session_file = "{config.colors.backend.session_file}"

[ui]
window_width = {config.ui.window_width}
window_height = {config.ui.window_height}
'''

    with open(CONFIG_FILE, "w") as f:
        f.write(content)
