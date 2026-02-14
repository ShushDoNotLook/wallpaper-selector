"""WallpaperThumbnail widget for displaying individual wallpaper previews"""

from pathlib import Path
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk, Gio, Pango


class WallpaperThumbnail(Gtk.Box):
    """Individual wallpaper thumbnail widget"""

    def __init__(self, path: Path, is_current: bool, on_activate_callback):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.wallpaper_path = path
        self.on_activate_callback = on_activate_callback
        self.is_current = is_current

        self.add_css_class("thumbnail")

        # Create preview image
        self.preview = Gtk.Picture()
        self.preview.set_content_fit(Gtk.ContentFit.COVER)
        self.preview.set_size_request(300, 180)
        self.preview.add_css_class("preview-image")
        self.append(self.preview)

        # Load image from file
        try:
            self.preview.set_file(Gio.File.new_for_path(str(path)))
        except:
            pass

        # Info overlay
        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        info_box.add_css_class("info-box")

        # Filename
        name_label = Gtk.Label()
        name_label.set_text(path.name[:25] + "..." if len(path.name) > 25 else path.name)
        name_label.set_halign(Gtk.Align.START)
        name_label.set_ellipsize(Pango.EllipsizeMode.END)
        name_label.add_css_class("filename")
        info_box.append(name_label)

        # Current indicator
        if is_current:
            current_badge = Gtk.Label()
            current_badge.set_text("● Current")
            current_badge.set_halign(Gtk.Align.END)
            current_badge.set_hexpand(True)
            current_badge.add_css_class("current-badge")
            info_box.append(current_badge)

        self.append(info_box)

        # Click handler
        click_ctrl = Gtk.GestureClick()
        click_ctrl.connect("pressed", self.on_clicked)
        self.add_controller(click_ctrl)

        # Key handler
        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect("key-pressed", self.on_key_pressed)
        self.add_controller(key_ctrl)

    def on_clicked(self, gesture, n_press, x, y):
        """Handle click"""
        if n_press == 1:
            self.on_activate_callback(self.wallpaper_path)
            return True
        return False

    def on_key_pressed(self, controller, keyval, keycode, state):
        """Handle key press"""
        if keyval == Gdk.KEY_Return or keyval == Gdk.KEY_KP_Enter:
            self.on_activate_callback(self.wallpaper_path)
            return True
        return False

    def set_current(self, is_current: bool):
        """Update current wallpaper indicator"""
        self.is_current = is_current
