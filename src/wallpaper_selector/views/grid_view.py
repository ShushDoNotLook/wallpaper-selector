"""Grid View - flowbox grid layout for wallpaper selection"""

from pathlib import Path
from typing import Optional, TYPE_CHECKING
from gi.repository import Gtk, Gdk

if TYPE_CHECKING:
    from wallpaper_selector.models.wallpaper_manager import WallpaperManager
    from wallpaper_selector.thumbnail import WallpaperThumbnail


class GridView(BaseView):
    """FlowBox-based grid view for wallpaper selection"""

    def __init__(self, wallpaper_manager: 'WallpaperManager'):
        super().__init__(wallpaper_manager)
        self.flow_box: Optional[Gtk.FlowBox] = None

    def build(self) -> Gtk.Widget:
        """Build the grid view"""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

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
        flowbox_key_ctrl.connect("key-pressed", self._on_flowbox_key_pressed)
        self.flow_box.add_controller(flowbox_key_ctrl)

        scroll.set_child(self.flow_box)
        container.append(scroll)

        # Grid hints at bottom
        grid_hints = Gtk.Label()
        grid_hints.set_text("Tab Carousel | Enter Set | Esc Close")
        grid_hints.add_css_class("carousel-hints")
        grid_hints.set_margin_top(8)
        grid_hints.set_margin_bottom(8)
        grid_hints.set_halign(Gtk.Align.CENTER)
        container.append(grid_hints)

        self.widget = container
        return container

    def update(self):
        """Refresh grid content"""
        # Clear existing children
        for child in self.flow_box.get_children():
            self.flow_box.remove(child)

        # Rebuild wallpaper thumbnails
        for wallpaper in self.wallpaper_manager.get_wallpapers():
            child = Gtk.FlowBoxChild()
            from wallpaper_selector.thumbnail import WallpaperThumbnail
            current = (str(wallpaper) == self.wallpaper_manager.get_current_wallpaper())
            child.set_child(WallpaperThumbnail(wallpaper, current, self.wallpaper_manager.set_wallpaper))
            self.flow_box.append(child)

        # Focus first item
        if self.flow_box.get_children():
            first_child = self.flow_box.get_child_at_index(0)
            if first_child:
                first_child.grab_focus()

    def handle_key_press(self, keyval: int) -> bool:
        """Handle grid-specific key presses"""
        if keyval == Gdk.KEY_Return or keyval == Gdk.KEY_KP_Enter:
            selected = self.flow_box.get_selected_children()
            if selected:
                child = selected[0]
                widget = child.get_child()
                if hasattr(widget, 'wallpaper_path'):
                    self.wallpaper_manager.set_wallpaper(widget.wallpaper_path)
                return True
        return False

    def _on_flowbox_key_pressed(self, controller, keyval, keycode, state):
        """Handle Enter key on flowbox to activate selected wallpaper"""
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            selected = self.flow_box.get_selected_children()
            if selected:
                child = selected[0]
                widget = child.get_child()
                if hasattr(widget, 'wallpaper_path'):
                    self.wallpaper_manager.set_wallpaper(widget.wallpaper_path)
                    return True
        return False
