import pyautogui
import numpy as np
import cv2
import threading

class ScreenCapture:
    def __init__(self):
        self.screen_size = pyautogui.size()
        self.frame = None
        self.previous_frame = None
        self.running = False
        self.thread = None

    def _capture_loop(self):
        while self.running:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
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