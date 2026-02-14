"""Main WallpaperSelector GTK Application"""

import subprocess
from pathlib import Path
from typing import List, Optional
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk, Gio, Pango

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
        self.carousel_mode = True
        self.carousel_index = 0
        self.carousel_container: Optional[Gtk.Box] = None
        self.carousel_image: Optional[Gtk.Picture] = None
        self.carousel_label: Optional[Gtk.Label] = None
        self.view_stack: Optional[Gtk.Stack] = None

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

    def toggle_view(self):
        """Toggle between grid and carousel view"""
        self.carousel_mode = not self.carousel_mode
        if self.carousel_mode:
            self.view_stack.set_visible_child_name("carousel")
            self.update_carousel()
        else:
            self.view_stack.set_visible_child_name("grid")

    def update_carousel(self):
        """Update carousel display with current index"""
        if not self.wallpapers or not self.carousel_image:
            return

        path = self.wallpapers[self.carousel_index]
        self.carousel_image.set_file(Gio.File.new_for_path(str(path)))

        if self.carousel_label:
            name = path.name
            current_marker = " (current)" if str(path) == self.current_wallpaper else ""
            self.carousel_label.set_text(f"{name}{current_marker}")

    def carousel_prev(self):
        """Go to previous wallpaper in carousel"""
        if not self.wallpapers:
            return
        self.carousel_index = (self.carousel_index - 1) % len(self.wallpapers)
        self.update_carousel()

    def carousel_next(self):
        """Go to next wallpaper in carousel"""
        if not self.wallpapers:
            return
        self.carousel_index = (self.carousel_index + 1) % len(self.wallpapers)
        self.update_carousel()

    def on_window_key_pressed(self, controller, keyval, keycode, state, window):
        """Handle window-level key presses"""
        if keyval == Gdk.KEY_Escape:
            window.close()
            return True
        elif keyval == Gdk.KEY_Tab:
            self.toggle_view()
            return True
        elif self.carousel_mode:
            if keyval == Gdk.KEY_Left:
                self.carousel_prev()
                return True
            elif keyval == Gdk.KEY_Right:
                self.carousel_next()
                return True
            elif keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
                if self.wallpapers:
                    self.set_wallpaper(self.wallpapers[self.carousel_index])
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

    def create_carousel_view(self) -> Gtk.Widget:
        """Create the carousel view"""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        container.set_margin_start(24)
        container.set_margin_end(24)
        container.set_margin_top(24)
        container.set_margin_bottom(24)
        container.set_valign(Gtk.Align.CENTER)
        container.set_halign(Gtk.Align.CENTER)

        # Main image
        self.carousel_image = Gtk.Picture()
        self.carousel_image.set_content_fit(Gtk.ContentFit.CONTAIN)
        self.carousel_image.set_size_request(800, 500)
        self.carousel_image.add_css_class("carousel-image")
        container.append(self.carousel_image)

        # Filename label
        self.carousel_label = Gtk.Label()
        self.carousel_label.add_css_class("carousel-label")
        self.carousel_label.set_margin_top(12)
        container.append(self.carousel_label)

        # Hints
        hints = Gtk.Label()
        hints.set_text("← → Navigate | Enter Set | Tab Grid | Esc Close")
        hints.add_css_class("carousel-hints")
        hints.set_margin_top(8)
        container.append(hints)

        self.carousel_container = container
        return container

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

        # View stack for switching between grid and carousel
        self.view_stack = Gtk.Stack()
        self.view_stack.set_vexpand(True)

        # Grid view
        grid_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

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
        grid_container.append(scroll)

        # Grid hints at bottom
        grid_hints = Gtk.Label()
        grid_hints.set_text("Tab Carousel | Enter Set | Esc Close")
        grid_hints.add_css_class("carousel-hints")
        grid_hints.set_margin_top(8)
        grid_hints.set_margin_bottom(8)
        grid_container.append(grid_hints)

        # Carousel view
        carousel_view = self.create_carousel_view()

        self.view_stack.add_named(grid_container, "grid")
        self.view_stack.add_named(carousel_view, "carousel")
        self.view_stack.set_visible_child_name("carousel")
        self.update_carousel()

        main_box.append(self.view_stack)

        # Add key handler to window (capture phase to intercept Tab before GTK)
        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        key_ctrl.connect("key-pressed", self.on_window_key_pressed, win)
        win.add_controller(key_ctrl)

        # Present window
        win.present()

        # Focus first item
        first_child = self.flow_box.get_child_at_index(0)
        if first_child:
            first_child.grab_focus()
