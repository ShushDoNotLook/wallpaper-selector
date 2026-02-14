"""Main WallpaperSelector GTK Application - Refactored with separated views"""

from pathlib import Path
from gi.repository import Gtk, Gdk

from .models.wallpaper_manager import WallpaperManager
from .views.carousel_view import CarouselView
from .views.grid_view import GridView
from .styles import CSS


class WallpaperSelector(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id='com.github.wallpaper-selector',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        # Initialize wallpaper manager
        wallpaper_dir = Path.home() / "Pictures" / "Wallpapers"
        self.wallpaper_manager = WallpaperManager(wallpaper_dir)

        # View management
        self.current_view = None  # 'carousel' or 'grid'
        self.carousel_view: Optional[CarouselView] = None
        self.grid_view: Optional[GridView] = None
        self.view_stack: Optional[Gtk.Stack] = None

    def get_current_wallpaper(self) -> Optional[str]:
        """Get current wallpaper from swww"""
        return self.wallpaper_manager.get_current_wallpaper()

    def load_wallpapers(self):
        """Load all wallpapers from directory"""
        return self.wallpaper_manager.get_wallpapers()

    def set_wallpaper(self, path: Path):
        """Set wallpaper using wallpaper manager"""
        self.wallpaper_manager.set_wallpaper(path)

    def toggle_view(self):
        """Toggle between grid and carousel view"""
        if self.current_view == 'carousel':
            self.current_view = 'grid'
            self.view_stack.set_visible_child_name("grid")
        else:
            self.current_view = 'carousel'
            self.view_stack.set_visible_child_name("carousel")

        # Update view after switching
        if self.current_view == 'carousel' and self.carousel_view:
            self.carousel_view.update()
        elif self.current_view == 'grid' and self.grid_view:
            self.grid_view.update()

    def on_window_key_pressed(self, controller, keyval, keycode, state, window):
        """Handle window-level key presses"""
        if keyval == Gdk.KEY_Escape:
            window.close()
            return True
        elif keyval == Gdk.KEY_Tab:
            self.toggle_view()
            return True

        # Delegate to current view for view-specific keys
        if self.current_view == 'carousel' and self.carousel_view:
            if self.carousel_view.handle_key_press(keyval):
                return True
        elif self.current_view == 'grid' and self.grid_view:
            if self.grid_view.handle_key_press(keyval):
                return True

        return False

    def do_activate(self):
        """Build and show the UI"""
        wallpapers = self.wallpaper_manager.get_wallpapers()

        if not wallpapers:
            dialog = Gtk.MessageDialog(
                transient_for=None,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="No Wallpapers Found"
            )
            dialog.format_secondary_text(
                f"Please add images to:\n{self.wallpaper_manager.wallpaper_dir}"
            )
            dialog.run()
            dialog.destroy()
            return

        # Create main window
        win = Gtk.ApplicationWindow(application=self)
        win.set_title("Wallpaper Selector")
        win.set_default_size(1100, 550)
        win.set_resizable(False)

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

        # Create views
        self.carousel_view = CarouselView(self.wallpaper_manager)
        self.grid_view = GridView(self.wallpaper_manager)

        # Add views to stack
        self.view_stack.add_named(self.grid_view.build(), "grid")
        self.view_stack.add_named(self.carousel_view.build(), "carousel")

        # Set initial view
        self.current_view = 'carousel'
        self.view_stack.set_visible_child_name("carousel")
        self.carousel_view.update()

        main_box.append(self.view_stack)

        # Add key handler to window (capture phase to intercept Tab before GTK)
        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        key_ctrl.connect("key-pressed", self.on_window_key_pressed, win)
        win.add_controller(key_ctrl)

        # Present window
        win.present()
