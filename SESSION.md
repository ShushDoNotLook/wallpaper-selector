# Wallpaper Selector - Session Summary

## Date: 2026-02-17

## Problem
Wallpaper and matugen colors were not syncing properly on boot:
- System had to wait several seconds to be usable
- Matugen colors didn't sync to the correct colors
- `swww` showed `jane-doe.jpg` but DMS session had stale `frieren.png`
- Sync service failed with "Wallpaper backend not ready after timeout"

## Root Causes
1. **Non-existent systemd dependency**: `wallpaper-selector-sync.service` had `After=swww.service` but `swww.service` doesn't exist (swww is started by Niri, not systemd)
2. **No subprocess timeout**: `swww query` could hang indefinitely when called before daemon was ready
3. **No wallpaper cache**: Sync had to query swww on every boot, which was unreliable

## Solution Implemented
Implemented a wallpaper caching system for instant boot sync:

### New Files
- **`src/wallpaper_selector/cache.py`**: Manages wallpaper cache in `~/.local/state/wallpaper-selector/last-wallpaper`

### Modified Files
- **`src/wallpaper_selector/models/wallpaper_manager.py`**: Now saves wallpaper to cache when setting
- **`src/wallpaper_selector/sync.py`**: Completely rewritten - reads from cache instead of querying swww, no more waiting for daemon
- **`src/wallpaper_selector/plugins/wallpaper/swww.py`**: Added 5s timeout to all subprocess calls for safety
- **`~/.config/systemd/user/wallpaper-selector-sync.service`**: Removed non-existent `swww.service` dependencies

## Benefits
- **Instant sync**: No waiting for swww daemon on boot
- **Colors loaded immediately**: DMS loads from cache, session updated with correct wallpaper path
- **Reliable**: Works regardless of swww startup timing
- **Safe**: Timeout prevents hanging subprocess calls

## Testing
```bash
# Seed cache with current wallpaper
mkdir -p ~/.local/state/wallpaper-selector
swww query | grep -oP 'image: \K.*' | head -1 > ~/.local/state/wallpaper-selector/last-wallpaper

# Test sync (should be instant)
wallpaper-selector sync --verbose

# Verify DMS session updated
cat ~/.local/state/DankMaterialShell/session.json | grep wallpaperPath
```

## Next Steps
- Reboot to verify the sync service works on boot
- Consider adding cache invalidation if wallpaper is deleted
