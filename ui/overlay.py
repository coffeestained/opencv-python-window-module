import gi
import subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class Overlay:
    def __init__(self, target_window_name):
        self.target_window_name = target_window_name
        self.window = Gtk.Window()
        self.setup_window()
        self.attach_to_target()

    def setup_window(self):
        self.window.set_app_paintable(True)
        self.window.set_decorated(False)
        self.window.set_keep_above(True)
        self.window.set_accept_focus(False)

        screen = self.window.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.window.set_visual(visual)

        self.window.connect('destroy', Gtk.main_quit)

    def attach_to_target(self):
        try:
            # Grab geometry of the target window
            cmd = ["xdotool", "search", "--name", self.target_window_name, "getwindowgeometry", "--shell"]
            result = subprocess.check_output(cmd, universal_newlines=True)
            geom = {}
            for line in result.strip().split('\n'):
                if '=' in line:
                    key, val = line.split('=')
                    geom[key.strip()] = int(val.strip())

            # Position and resize the overlay window
            self.window.move(geom['X'], geom['Y'])
            self.window.set_default_size(geom['WIDTH'], geom['HEIGHT'])

            # Add a default label for now
            label = Gtk.Label(label="🔥 Overlay Attached 🔥")
            self.window.add(label)

        except subprocess.CalledProcessError:
            print(f"[!] Failed to find or attach to window: {self.target_window_name}")

    def show(self):
        self.window.show_all()
        Gtk.main()

