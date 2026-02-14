# Wallpaper Selector

Modern GTK4 wallpaper selector for Wayland/Niri with swww and DMS integration.

## Features

- Grid preview of all wallpapers in `~/Pictures/Wallpapers`
- Keyboard navigation (arrow keys, Enter to select, Esc to close)
- Toggle behavior: press Super+Shift+W to open/close
- Automatic color scheme generation via DMS matugen integration
- Sorted by modification time (newest first)

## Installation

```bash
uv tool install -e ~/dev/wallpaper-selector
```

## Usage

### From Terminal
```bash
wallpaper-selector
```

### From Niri Keybinding
Press `Super+Shift+W` to toggle the selector.

## Key Bindings

| Key | Action |
|-----|--------|
| Arrow keys | Navigate wallpapers |
| Enter | Set selected wallpaper |
| Escape | Close selector |

## Requirements

- GTK4 with PyGObject
- swww (for setting wallpapers)
- DMS (DankMaterialShell) for color generation
- Niri (optional, for keybinding)

## Files

- `~/.local/bin/wallpaper-selector` - Installed executable
- `~/Pictures/Wallpapers/` - Wallpaper directory
