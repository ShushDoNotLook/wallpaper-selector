"""Carousel View - 3D carousel with preview thumbnails"""

from pathlib import Path
from typing import Optional, TYPE_CHECKING
from gi.repository import Gtk, Gdk, Gio

if TYPE_CHECKING:
    from wallpaper_selector.models.wallpaper_manager import WallpaperManager

from wallpaper_selector.views.base_view import BaseView


class CarouselView(BaseView):
    """3D carousel view with left/right preview thumbnails"""

    def __init__(self, wallpaper_manager: 'WallpaperManager'):
        super().__init__(wallpaper_manager)
        self.carousel_index = self._find_current_wallpaper_index()

        # Carousel widgets
        self.preview_left: Optional[Gtk.Picture] = None
        self.preview_right: Optional[Gtk.Picture] = None
        self.preview_left_box: Optional[Gtk.Box] = None
        self.preview_right_box: Optional[Gtk.Box] = None
        self.carousel_image: Optional[Gtk.Picture] = None
        self.carousel_label: Optional[Gtk.Label] = None

    def _find_current_wallpaper_index(self) -> int:
        """Find the index of the current wallpaper in the wallpapers list"""
        current = self.wallpaper_manager.get_current_wallpaper()
        if current:
            wallpapers = self.wallpaper_manager.get_wallpapers()
            for i, path in enumerate(wallpapers):
                if str(path) == current:
                    return i
        return 0  # Default to first wallpaper if not found

    def build(self) -> Gtk.Widget:
        """Build the carousel view"""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        container.set_margin_start(16)
        container.set_margin_end(16)
        container.set_margin_top(24)
        container.set_margin_bottom(16)
        container.set_valign(Gtk.Align.CENTER)
        container.set_halign(Gtk.Align.CENTER)

        # Image row (left preview, main image, right preview)
        image_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        image_row.set_valign(Gtk.Align.CENTER)
        image_row.set_halign(Gtk.Align.CENTER)

        # Left preview thumbnail (clickable)
        self.preview_left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.preview_left_box.set_margin_end(24)
        self.preview_left_box.set_valign(Gtk.Align.CENTER)
        self.preview_left_box.add_css_class("preview-thumbnail-box")
        self.preview_left_box.add_css_class("preview-left-3d")

        self.preview_left = Gtk.Picture()
        self.preview_left.set_content_fit(Gtk.ContentFit.COVER)
        self.preview_left.set_size_request(200, 125)
        self.preview_left.set_valign(Gtk.Align.CENTER)
        self.preview_left.add_css_class("preview-thumbnail")
        self.preview_left_box.append(self.preview_left)

        left_click = Gtk.GestureClick()
        left_click.connect("pressed", self._on_preview_left_clicked)
        self.preview_left_box.add_controller(left_click)

        image_row.append(self.preview_left_box)

        # Left navigation icon
        left_nav_icon = Gtk.Label()
        left_nav_icon.set_text("◀")
        left_nav_icon.add_css_class("nav-icon")
        left_nav_icon.set_valign(Gtk.Align.CENTER)
        image_row.append(left_nav_icon)

        # Main image (center)
        main_image_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_image_box.set_margin_start(12)
        main_image_box.set_margin_end(12)
        main_image_box.set_valign(Gtk.Align.CENTER)
        main_image_box.add_css_class("carousel-main-3d")

        self.carousel_image = Gtk.Picture()
        self.carousel_image.set_content_fit(Gtk.ContentFit.COVER)
        self.carousel_image.set_size_request(600, 375)
        self.carousel_image.set_valign(Gtk.Align.CENTER)
        self.carousel_image.add_css_class("carousel-image")
        main_image_box.append(self.carousel_image)

        image_row.append(main_image_box)

        # Right navigation icon
        right_nav_icon = Gtk.Label()
        right_nav_icon.set_text("▶")
        right_nav_icon.add_css_class("nav-icon")
        right_nav_icon.set_valign(Gtk.Align.CENTER)
        image_row.append(right_nav_icon)

        # Right preview thumbnail (clickable)
        self.preview_right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.preview_right_box.set_margin_start(24)
        self.preview_right_box.set_valign(Gtk.Align.CENTER)
        self.preview_right_box.add_css_class("preview-thumbnail-box")
        self.preview_right_box.add_css_class("preview-right-3d")

        self.preview_right = Gtk.Picture()
        self.preview_right.set_content_fit(Gtk.ContentFit.COVER)
        self.preview_right.set_size_request(200, 125)
        self.preview_right.set_valign(Gtk.Align.CENTER)
        self.preview_right.add_css_class("preview-thumbnail")
        self.preview_right_box.append(self.preview_right)

        right_click = Gtk.GestureClick()
        right_click.connect("pressed", self._on_preview_right_clicked)
        self.preview_right_box.add_controller(right_click)

        image_row.append(self.preview_right_box)
        container.append(image_row)

        # Filename label
        self.carousel_label = Gtk.Label()
        self.carousel_label.add_css_class("carousel-label")
        self.carousel_label.set_margin_top(6)
        container.append(self.carousel_label)

        # Hints
        hints = Gtk.Label()
        hints.set_text("← → Navigate | Enter Set | Tab Grid | Esc Close")
        hints.add_css_class("carousel-hints")
        hints.set_margin_top(4)
        hints.set_size_request(500, -1)
        hints.set_halign(Gtk.Align.CENTER)
        container.append(hints)

        self.widget = container
        return container

    def update(self):
        """Update carousel display with current index"""
        wallpapers = self.wallpaper_manager.get_wallpapers()
        if not wallpapers or not self.carousel_image:
            return

        path = wallpapers[self.carousel_index]
        self.carousel_image.set_file(Gio.File.new_for_path(str(path)))

        if self.carousel_label:
            name = path.name
            current_marker = " (current)" if str(path) == self.wallpaper_manager.get_current_wallpaper() else ""
            self.carousel_label.set_text(f"{name}{current_marker}")

        # Update preview thumbnails
        self._update_preview_thumbnails()

    def _update_preview_thumbnails(self):
        """Update preview thumbnails with prev/next wallpapers"""
        wallpapers = self.wallpaper_manager.get_wallpapers()
        if not wallpapers:
            return

        # Handle edge cases based on number of wallpapers
        if len(wallpapers) <= 1:
            self.preview_left_box.set_visible(False)
            self.preview_right_box.set_visible(False)
            return

        # Show previews for 2+ wallpapers
        self.preview_left_box.set_visible(True)
        self.preview_right_box.set_visible(True)

        # Calculate prev/next indices with wraparound
        prev_index = (self.carousel_index - 1) % len(wallpapers)
        next_index = (self.carousel_index + 1) % len(wallpapers)

        # Update left preview (previous wallpaper)
        prev_path = wallpapers[prev_index]
        self.preview_left.set_file(Gio.File.new_for_path(str(prev_path)))

        # Update right preview (next wallpaper)
        next_path = wallpapers[next_index]
        self.preview_right.set_file(Gio.File.new_for_path(str(next_path)))

    def navigate_prev(self):
        """Go to previous wallpaper in carousel"""
        wallpapers = self.wallpaper_manager.get_wallpapers()
        if not wallpapers:
            return
        self.carousel_index = (self.carousel_index - 1) % len(wallpapers)
        self.update()

    def navigate_next(self):
        """Go to next wallpaper in carousel"""
        wallpapers = self.wallpaper_manager.get_wallpapers()
        if not wallpapers:
            return
        self.carousel_index = (self.carousel_index + 1) % len(wallpapers)
        self.update()

    def _on_preview_left_clicked(self, gesture, n_press, x, y):
        """Handle left preview thumbnail click"""
        if n_press == 1:
            self.navigate_prev()

    def _on_preview_right_clicked(self, gesture, n_press, x, y):
        """Handle right preview thumbnail click"""
        if n_press == 1:
            self.navigate_next()

    def handle_key_press(self, keyval: int) -> bool:
        """Handle carousel-specific key presses"""
        wallpapers = self.wallpaper_manager.get_wallpapers()
        if not wallpapers:
            return False

        if keyval == Gdk.KEY_Left:
            self.navigate_prev()
            return True
        elif keyval == Gdk.KEY_Right:
            self.navigate_next()
            return True
        elif keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            if wallpapers:
                self.wallpaper_manager.set_wallpaper(wallpapers[self.carousel_index])
            return True
        return False

    def activate_wallpaper(self):
        """Activate/set the current wallpaper"""
        wallpapers = self.wallpaper_manager.get_wallpapers()
        if wallpapers:
            return self.wallpaper_manager.set_wallpaper(wallpapers[self.carousel_index])
