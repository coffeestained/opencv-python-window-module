import os
import cv2
from utils.logging import logger
import subprocess
import numpy as np
import mss
import threading
from gi.repository import Gtk, GLib, GdkPixbuf
from PIL import Image
from dotenv import load_dotenv
import subprocess
import numpy as np
import cv2
from PIL import Image
import io
load_dotenv()

PREVIEW_WIDTH = 600

class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()
        self.capture_method = "screen"
        self.window_id = None
        self.frame = None
        self.previous_frame = None
        self.running = False
        self.thread = None

    def set_capture_target(self, target):
        logger.debug(f"Setting capture target to: {target}")
        if target == "Screen":
            self.capture_method = "screen"
            self.window_id = None
        else:
            self.capture_method = "window"
            self.window_id = target
        self.stop()
        self.start()   

    # Capture the window using xdotool and ffmpeg
    # As a note this is really slow, not safe, inputs are not sanitized and as a result not recommended for production.
    # I needed a way to capture the window annd came up with this.
    # TODO: Find a better way to capture the window.
    def capture_window(self):
        try:
            result = subprocess.run(
                ['xdotool', 'search', '--name', self.window_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            window_ids = result.stdout.strip().split('\n')
            if not window_ids:
                logger.error(f"[xdotool] No window ID found for name: {self.window_id}")
                return None
            window_id = window_ids[0]

            # Get geometry using xwininfo
            wininfo = subprocess.run(['xwininfo', '-id', window_id], stdout=subprocess.PIPE, text=True)
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
                logger.error(f"[ffmpeg ERROR] {proc.stderr.decode()}")
                return None

            image = Image.open(io.BytesIO(proc.stdout))
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        except Exception as e:
            logger.error(f"Error capturing window: {e}")
            return None

    def capture_screen(self, mssRef):
        try:
            
            monitor = mssRef.monitors[1]  # [0] = all, [1] = primary
            sct_img = mssRef.grab(monitor)
            frame = np.array(sct_img)
            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            return self.frame
        except Exception as e:
            logger.error(f"Error capturing screen: {e}")
            return None


    def _capture_loop(self):
        mssRef = mss.mss()
        while self.running:
            if self.capture_method == "window" and self.window_id:
                frame = self.capture_window()
            else:
                frame = self.capture_screen(mssRef)
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
            self.thread.join(1)

    def get_frame(self):
        return self.frame

    def get_previous_frame(self):
        return self.previous_frame
