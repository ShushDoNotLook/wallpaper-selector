# Wallpaper Selector

Modern GTK4 wallpaper selector for Wayland/Niri with swww and DMS integration.

## Changelog

### v1.1.0
- Added `wallpaper-selector sync` command to fix DMS using wrong wallpaper colors on boot
- Added systemd service for automatic sync on login

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

## Boot Sync Setup (Fixes DMS using wrong wallpaper colors)

To sync your current wallpaper to DMS on boot (prevents index 0 fallback):

```bash
cd ~/dev/wallpaper-selector
./install-sync.sh
```

This installs a systemd service that:
1. Waits for swww-daemon to be ready
2. Queries the current wallpaper from swww
3. Syncs it to DMS matugen for proper color generation

## Usage

### From Terminal
```bash
wallpaper-selector          # Open GTK selector
wallpaper-selector sync    # Sync current wallpaper to DMS (one-time)
wallpaper-selector sync -v # Sync with verbose output
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
