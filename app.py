import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pynput import keyboard
from utils.screen import ScreenCapture
from ui.overlay import Overlay

# Load environment variables from .env file
load_dotenv()

# App Class
class App:
    def __init__(self):
        self.screen = ScreenCapture()
        self.overlay = Overlay()
        self.listener = keyboard.Listener(
            on_release=self.on_release,
        )
        self.executor = ThreadPoolExecutor()
        self.loop = asyncio.new_event_loop()
        
    # Listens for a escape key release and then closes the program
    def on_release(self, key):
        if key == keyboard.Key.esc:
            os._exit(0)

    def run(self):
        self.listener.start()  # Start the listener (non-async)
        self.overlay.register_frame_source(self.screen)
        self.overlay.capture_target_callback = self.screen.set_capture_target
        self.loop.run_in_executor(self.executor, self.screen.start)  # start screen capture in another thread
        self.loop.run_in_executor(self.executor, self.overlay.show)  # start GTK in another thread

        self.loop.run_forever()

# Run the App
if __name__ == "__main__":
    app = App()
    app.run()