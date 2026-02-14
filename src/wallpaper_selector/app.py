"""Main WallpaperSelector GTK Application"""

import subprocess
from pathlib import Path
from typing import List, Optional
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk, Gio

from .thumbnail import WallpaperThumbnail
from .styles import CSS


class WallpaperSelector(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id='com.github.wallpaper-selector',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.wallpaper_dir = Path.home() / "Pictures" / "Wallpapers"
        self.current_wallpaper = self.get_current_wallpaper()
        self.wallpapers: List[Path] = []
        self.flow_box: Optional[Gtk.FlowBox] = None

    def get_current_wallpaper(self) -> Optional[str]:
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
        except:
            pass
        return None

    def load_wallpapers(self):
        """Load all wallpapers from directory"""
        if not self.wallpaper_dir.exists():
            self.wallpaper_dir.mkdir(parents=True, exist_ok=True)
            return []

        extensions = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'}
        wallpapers = sorted(
            [f for f in self.wallpaper_dir.iterdir()
             if f.suffix.lower() in extensions],
            key=lambda x: x.stat().st_mtime,
            reverse=True  # newest first
        )
        self.wallpapers = wallpapers

    def set_wallpaper(self, path: Path):
        """Set wallpaper using swww and regenerate colors via DMS"""
        try:
            # Set wallpaper with swww
            subprocess.run(
                ['swww', 'img', str(path), '--transition-type', 'grow',
                 '--transition-duration', '0.7', '--transition-fps', '144'],
                check=True
            )

            # Generate colors via DMS matugen integration
            subprocess.run(
                ['dms', 'matugen', 'queue',
                 '--state-dir', Path.home() / '.cache/DankMaterialShell',
                 '--config-dir', Path.home() / '.config/DankMaterialShell',
                 '--shell-dir', '/usr/share/quickshell/dms',
                 '--value', str(path)],
                check=False
            )

            # Update selection indicator
            if self.flow_box:
                for child in self.flow_box.get_children():
                    widget = child.get_child()
                    if hasattr(widget, 'wallpaper_path') and widget.wallpaper_path == path:
                        widget.set_current(True)
                    else:
                        widget.set_current(False)
        except Exception as e:
            print(f"Error setting wallpaper: {e}")

    def on_window_key_pressed(self, controller, keyval, keycode, state, window):
        """Handle window-level key presses (ESC to close)"""
        if keyval == Gdk.KEY_Escape:
            window.close()
            return True
        return False

    def on_flowbox_key_pressed(self, controller, keyval, keycode, state):
        """Handle Enter key on flowbox to activate selected wallpaper"""
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            selected = self.flow_box.get_selected_children()
            if selected:
                child = selected[0]
                widget = child.get_child()
                if hasattr(widget, 'wallpaper_path'):
                    self.set_wallpaper(widget.wallpaper_path)
                    return True
        return False

    def create_wallpaper_thumbnail(self, path: Path) -> Gtk.Widget:
        """Create a thumbnail widget for a wallpaper"""
        current = path == Path(self.current_wallpaper) if self.current_wallpaper else False
        return WallpaperThumbnail(path, current, self.set_wallpaper)

    def do_activate(self):
        """Build and show the UI"""
        self.load_wallpapers()

        if not self.wallpapers:
            dialog = Gtk.MessageDialog(
                transient_for=None,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="No Wallpapers Found"
            )
            dialog.format_secondary_text(
                f"Please add images to:\n{self.wallpaper_dir}"
            )
            dialog.run()
            dialog.destroy()
            return

        # Create main window
        win = Gtk.ApplicationWindow(application=self)
        win.set_title("Wallpaper Selector")
        win.set_default_size(1200, 800)
        win.set_resizable(True)

        # Setup CSS for styling
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        win.set_child(main_box)

        # Header bar
        header = self.create_header_bar(win)
        main_box.append(header)

        # Search/Filter bar
        search_box = self.create_search_bar()
        main_box.append(search_box)

        # Scrollable content
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        # Flow box for grid layout
        self.flow_box = Gtk.FlowBox()
        self.flow_box.set_selection_mode(Gtk.SelectionMode.BROWSE)
        self.flow_box.set_homogeneous(True)
        self.flow_box.set_min_children_per_line(3)
        self.flow_box.set_max_children_per_line(6)
        self.flow_box.set_row_spacing(8)
        self.flow_box.set_column_spacing(8)
        self.flow_box.set_margin_start(12)
        self.flow_box.set_margin_end(12)
        self.flow_box.set_margin_top(12)
        self.flow_box.set_margin_bottom(12)

        # Handle Enter key on flowbox to activate selected item
        flowbox_key_ctrl = Gtk.EventControllerKey()
        flowbox_key_ctrl.connect("key-pressed", self.on_flowbox_key_pressed)
        self.flow_box.add_controller(flowbox_key_ctrl)

        # Add wallpaper thumbnails
        for wallpaper in self.wallpapers:
            child = Gtk.FlowBoxChild()
            child.set_child(self.create_wallpaper_thumbnail(wallpaper))
            self.flow_box.append(child)

        scroll.set_child(self.flow_box)
        main_box.append(scroll)

        # Status bar
        status_bar = self.create_status_bar()
        main_box.append(status_bar)

        # Add ESC key handler to close window
        esc_ctrl = Gtk.EventControllerKey()
        esc_ctrl.connect("key-pressed", self.on_window_key_pressed, win)
        win.add_controller(esc_ctrl)

        # Present window
        win.present()

        # Focus first item
        first_child = self.flow_box.get_child_at_index(0)
        if first_child:
            first_child.grab_focus()

    def create_header_bar(self, window):
        """Create the header bar with title and close button"""
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header.add_css_class("header")

        # Title
        title = Gtk.Label()
        title.set_text("Wallpaper Selector")
        title.add_css_class("title")
        header.append(title)

        header.append(Gtk.Box())

        # Key hints
        hints = Gtk.Label()
        hints.set_text("Navigate | Enter Set | Esc Close")
        hints.add_css_class("hints")
        header.append(hints)

        return header

    def create_search_bar(self):
        """Create search/filter bar"""
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        search_box.add_css_class("search-bar")
        search_box.set_margin_start(12)
        search_box.set_margin_end(12)
        search_box.set_margin_top(8)
        search_box.set_margin_bottom(8)

        return search_box

    def create_status_bar(self):
        """Create status bar with wallpaper count"""
        status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        status.add_css_class("status-bar")

        label = Gtk.Label()
        label.set_text(f"{len(self.wallpapers)} wallpapers")
        label.add_css_class("status-text")
        status.append(label)

        return status
