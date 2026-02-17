"""Wallpaper cache - stores last known wallpaper for fast boot sync"""

import hashlib
from pathlib import Path
from typing import Iterator

from gi.repository import Gdk, GdkPixbuf, Gio, GLib

CACHE_DIR = Path.home() / ".local" / "state" / "wallpaper-selector"
CACHE_FILE = CACHE_DIR / "last-wallpaper"
THUMBNAIL_DIR = CACHE_DIR / "thumbnails"
THUMBNAIL_SIZE = 200  # Width in pixels


def get_cached_wallpaper() -> str | None:
    """Get last cached wallpaper path"""
    if not CACHE_FILE.exists():
        return None
    try:
        path = CACHE_FILE.read_text().strip()
        # Verify the file still exists
        if Path(path).exists():
            return path
    except Exception:
        pass
    return None


def cache_wallpaper(path: str | Path) -> None:
    """Cache wallpaper path for next boot"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(str(path))


def _get_thumbnail_path(image_path: Path) -> Path:
    """Get the cached thumbnail path for an image"""
    # Use hash of absolute path to create unique filename
    path_hash = hashlib.md5(str(image_path.absolute()).encode()).hexdigest()
    return THUMBNAIL_DIR / f"{path_hash}.png"


def _is_thumbnail_valid(thumbnail_path: Path, original_path: Path) -> bool:
    """Check if cached thumbnail is still valid (exists and newer than original)"""
    if not thumbnail_path.exists():
        return False
    return thumbnail_path.stat().st_mtime >= original_path.stat().st_mtime


def _generate_thumbnail(image_path: Path, thumbnail_path: Path) -> bool:
    """Generate a thumbnail for an image. Returns True on success."""
    try:
        # Load original image
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(image_path))
        orig_width = pixbuf.get_width()
        orig_height = pixbuf.get_height()

        # Calculate new dimensions maintaining aspect ratio
        scale = THUMBNAIL_SIZE / orig_width
        new_width = THUMBNAIL_SIZE
        new_height = int(orig_height * scale)

        # Scale down
        scaled = pixbuf.scale_simple(new_width, new_height, GdkPixbuf.InterpType.BILINEAR)

        # Save as PNG
        scaled.savev(str(thumbnail_path), "png", [], [])
        return True
    except Exception as e:
        print(f"Error generating thumbnail for {image_path}: {e}")
        return False


def get_thumbnail(image_path: Path) -> Path | None:
    """Get thumbnail path, generating if needed. Returns None on failure."""
    THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

    thumbnail_path = _get_thumbnail_path(image_path)

    # Return cached thumbnail if valid
    if _is_thumbnail_valid(thumbnail_path, image_path):
        return thumbnail_path

    # Generate new thumbnail
    if _generate_thumbnail(image_path, thumbnail_path):
        return thumbnail_path
    return None


def ensure_thumbnails(image_paths: list[Path]) -> None:
    """Pre-generate thumbnails for all images (no-op if already cached)"""
    THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

    for image_path in image_paths:
        thumbnail_path = _get_thumbnail_path(image_path)
        if not _is_thumbnail_valid(thumbnail_path, image_path):
            _generate_thumbnail(image_path, thumbnail_path)


def ensure_thumbnails_async(image_paths: list[Path], callback=None) -> None:
    """Pre-generate thumbnails in background using idle handler.

    Args:
        image_paths: List of image paths to generate thumbnails for
        callback: Optional callback when all thumbnails are done
    """
    THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

    paths_to_generate = [
        (path, _get_thumbnail_path(path))
        for path in image_paths
        if not _is_thumbnail_valid(_get_thumbnail_path(path), path)
    ]

    if not paths_to_generate:
        if callback:
            callback()
        return

    generator = iter(paths_to_generate)

    def generate_one():
        try:
            image_path, thumbnail_path = next(generator)
            _generate_thumbnail(image_path, thumbnail_path)
            # Schedule next thumbnail
            GLib.idle_add(generate_one)
        except StopIteration:
            # All done
            if callback:
                callback()

    # Start generation
    GLib.idle_add(generate_one)
