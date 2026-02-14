"""CSS styles for wallpaper selector UI"""

import json
from pathlib import Path


def load_matugen_colors() -> dict:
    """Load matugen colors from DMS cache"""
    cache_file = Path.home() / ".cache" / "DankMaterialShell" / "dms-colors.json"
    try:
        with open(cache_file) as f:
            data = json.load(f)
            return data.get("colors", {}).get("dark", {})
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to default colors
        return {
            "background": "#1a1b26",
            "surface": "#16161e",
            "on_surface": "#c0caf5",
            "on_surface_variant": "#565f89",
            "primary": "#7aa2f7",
            "secondary": "#bb9af7",
            "tertiary": "#7dcfff",
            "outline": "#565f89",
            "surface_variant": "#1f2335",
        }


def generate_css(colors: dict) -> str:
    """Generate CSS with matugen colors"""
    # Extract colors with fallbacks
    background = colors.get("background", "#1a1b26")
    surface = colors.get("surface", "#16161e")
    surface_variant = colors.get("surface_variant", "#1f2335")
    on_surface = colors.get("on_surface", "#c0caf5")
    on_surface_variant = colors.get("on_surface_variant", "#565f89")
    primary = colors.get("primary", "#7aa2f7")
    tertiary = colors.get("tertiary", "#7dcfff")
    outline = colors.get("outline", "#565f89")

    # Convert hex to rgb for rgba values
    def hex_to_rgb(hex_color: str) -> tuple:
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgba(hex_color: str, alpha: float) -> str:
        r, g, b = hex_to_rgb(hex_color)
        return f"rgba({r}, {g}, {b}, {alpha})"

    return f"""
window {{
    background-color: {background};
    border-radius: 12px;
}}

.status-bar {{
    padding: 8px 20px;
    background-color: {surface};
    border-top: 1px solid {outline};
}}

.status-text {{
    font-size: 12px;
    color: {on_surface_variant};
}}

flowbox {{
    background-color: transparent;
}}

flowboxchild {{
    background-color: transparent;
    outline: none;
    padding: 4px;
}}

flowboxchild:focus {{
    outline: none;
}}

flowboxchild:focus .thumbnail {{
    outline: 2px solid {primary};
    outline-offset: 2px;
    border-radius: 8px;
}}

.thumbnail {{
    background-color: {background};
    border-radius: 8px;
    padding: 8px;
    transition: all 150ms ease;
}}

.thumbnail:hover {{
    background-color: {rgba(primary, 0.15)};
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}}

.preview-image {{
    border-radius: 6px;
    background-color: {background};
}}

.info-box {{
    padding: 4px 0;
}}

.filename {{
    font-size: 11px;
    color: {on_surface};
}}

.current-badge {{
    font-size: 10px;
    color: {tertiary};
    font-weight: 600;
}}

.carousel-image {{
    border-radius: 12px;
}}

.carousel-label {{
    font-size: 14px;
    color: {on_surface};
}}

.carousel-hints {{
    font-size: 11px;
    color: {on_surface_variant};
}}

/* Navigation icons */
.nav-icon {{
    font-size: 24px;
    color: {on_surface};
    opacity: 0.6;
    padding: 0 2px;
}}

/* Left preview - appears behind and to the left */
.preview-left-3d .preview-thumbnail {{
    opacity: 0.60;
    box-shadow: -6px 0 20px rgba(0, 0, 0, 0.6);
    transition: opacity 0.25s ease, box-shadow 0.25s ease;
}}

.preview-left-3d:hover .preview-thumbnail {{
    opacity: 1.0;
    box-shadow: -3px 0 12px rgba(0, 0, 0, 0.5);
}}

/* Main image - center stage, pops forward */
.carousel-main-3d .carousel-image {{
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.7);
}}

/* Right preview - appears behind and to the right */
.preview-right-3d .preview-thumbnail {{
    opacity: 0.60;
    box-shadow: 6px 0 20px rgba(0, 0, 0, 0.6);
    transition: opacity 0.25s ease, box-shadow 0.25s ease;
}}

.preview-right-3d:hover .preview-thumbnail {{
    opacity: 1.0;
    box-shadow: 3px 0 12px rgba(0, 0, 0, 0.5);
}}

.preview-thumbnail-box {{
    padding: 0;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.2s ease;
}}

.preview-thumbnail-box:hover {{
    background-color: {rgba(primary, 0.15)};
}}

.preview-thumbnail {{
    border-radius: 6px;
    border: none;
}}
"""


# Load default CSS for fallback
CSS = generate_css(load_matugen_colors())
