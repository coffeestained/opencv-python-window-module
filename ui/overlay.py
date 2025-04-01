import gi
gi.require_version('Gtk', '3.0')
import cv2
import subprocess
from utils.logging import logger
from gi.repository import Gtk, GLib, GdkPixbuf
from dotenv import load_dotenv
load_dotenv()

PREVIEW_WIDTH = 600

class Overlay:
    def __init__(self, capture_target_callback=None):
        self.preview_visible = True
        self.frame_source = None
        self.workflow_engine = None
        self.window = Gtk.Window()
        self.image = Gtk.Image()
        self.overlay_box = Gtk.Fixed()
        self.capture_selector = Gtk.ComboBoxText()
        self.capture_target_callback = capture_target_callback
        self.setup_window()
        self.setup_ui_components()
        self.populate_window_list()

    def setup_window(self):
        self.window.set_app_paintable(True)
        self.window.set_decorated(False)
        self.window.set_keep_above(True)
        self.window.set_accept_focus(False)
        self.window.stick()

        screen = self.window.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.window.set_visual(visual)

        self.window.add(self.overlay_box)
        self.window.connect('destroy', Gtk.main_quit)

    def setup_ui_components(self):
        label = Gtk.Label(label="OpenCV Toolbox")
        self.overlay_box.put(label, 10, 10)
        self.overlay_box.put(self.image, 10, 70)

        toggle_button = Gtk.Button(label="Show/Hide")
        toggle_button.connect("clicked", self.toggle_preview_visibility)
        self.overlay_box.put(toggle_button, 10, 40)

        self.capture_selector.append_text("Screen")
        self.capture_selector.set_active(0)
        self.capture_selector.connect("changed", self.capture_selection_changed)
        self.overlay_box.put(self.capture_selector, 150, 40)

    def populate_window_list(self):
        window_list = self.get_open_windows()
        for window_name in window_list:
            self.capture_selector.append_text(window_name)

    def get_open_windows(self):
        result = subprocess.run(['wmctrl', '-l'], stdout=subprocess.PIPE, text=True)
        windows = []
        for line in result.stdout.splitlines():
            parts = line.split(None, 3)
            if len(parts) == 4:
                windows.append(parts[3])
        return windows

    def capture_selection_changed(self, combo):
        selection = combo.get_active_text()
        logger.info(f"Selection: {selection}")
        if self.capture_target_callback:
            self.capture_target_callback(selection)

    def toggle_preview_visibility(self, button):
        self.preview_visible = not self.preview_visible
        self.image.set_visible(self.preview_visible)

    def register_frame_source(self, source_class):
        self.frame_source = source_class
        GLib.timeout_add(33, self.update_frame)

    def register_workflow_engine(self, workflow_engine):
        self.workflow_engine = workflow_engine

    def update_frame(self):
        if self.frame_source and hasattr(self.frame_source, 'frame') and self.preview_visible:
            frame = self.frame_source.frame
            if frame is not None:
                height, width = frame.shape[:2]
                if width > PREVIEW_WIDTH:
                    scale_ratio = PREVIEW_WIDTH / width
                    width = PREVIEW_WIDTH
                    height = int(height * scale_ratio)
                    frame = cv2.resize(frame, (width, height))

                pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                    frame.tobytes(),
                    GdkPixbuf.Colorspace.RGB,
                    False,
                    8,
                    width,
                    height,
                    width * 3
                )

                self.image.set_from_pixbuf(pixbuf)

        return True

    def show(self):
        self.window.show_all()
        Gtk.main()
