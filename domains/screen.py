import gi
gi.require_version('Gtk', '3.0')
import cv2
import subprocess
import numpy as np
import threading
from gi.repository import Gtk, GLib, GdkPixbuf
from PIL import Image
from dotenv import load_dotenv
import io
import mss
import os
load_dotenv()

PREVIEW_WIDTH = 600

class ScreenCapture:
    def __init__(self):
        self.capture_method = "screen"
        self.window_name = None
        self.window_id = None
        self.frame = None
        self.previous_frame = None
        self.running = False
        self.thread = None

    def set_capture_target(self, target):
        if target == "Screen":
            self.capture_method = "screen"
            self.window_name = None
            self.window_id = None
        else:
            self.capture_method = "window"
            self.window_name = target
            if not self.window_id:
                self.window_id = self.resolve_window_id(self.window_name)

    def resolve_window_id(self, name):
        try:
            result = subprocess.run(
                ['xdotool', 'search', '--name', name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            window_ids = result.stdout.strip().split('\n')
            return window_ids[0] if window_ids else None
        except subprocess.CalledProcessError as e:
            print(f"[xdotool ERROR] {e.stderr}")
            return None

    def capture_window(self):
        try:
            if not self.window_id:
                print("[capture_window] No window ID available.")
                return None

            # Get geometry using xwininfo
            wininfo = subprocess.run(['xwininfo', '-id', self.window_id], stdout=subprocess.PIPE, text=True)
            output = wininfo.stdout
            x = int([line for line in output.splitlines() if "Absolute upper-left X" in line][0].split()[-1])
            y = int([line for line in output.splitlines() if "Absolute upper-left Y" in line][0].split()[-1])
            width = int([line for line in output.splitlines() if "Width:" in line][0].split()[-1])
            height = int([line for line in output.splitlines() if "Height:" in line][0].split()[-1])

            # Build ffmpeg command
            ffmpeg_cmd = [
                'ffmpeg',
                '-f', 'x11grab',
                '-video_size', f'{width}x{height}',
                '-i', f'{os.environ.get("DISPLAY", ":0.0")}+{x},{y}',
                '-vframes', '1',
                '-f', 'image2pipe',
                '-vcodec', 'png',
                '-'
            ]

            proc = subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if proc.returncode != 0:
                print(f"[ffmpeg ERROR] {proc.stderr.decode()}")
                return None

            image = Image.open(io.BytesIO(proc.stdout))
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        except Exception as e:
            print(f"[General ERROR] {e}")
            return None

    def capture_screen(self):
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            frame = np.array(sct_img)
            return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    def _capture_loop(self):
        while self.running:
            if self.capture_method == "window" and self.window_id:
                frame = self.capture_window()
            else:
                frame = self.capture_screen()

            if frame is not None:
                self.previous_frame = self.frame
                self.frame = frame

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._capture_loop)
            self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            self.thread.join()

    def get_frame(self):
        return self.frame

    def get_previous_frame(self):
        return self.previous_frame
