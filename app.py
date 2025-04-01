import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pynput import keyboard
from domains.computer_vision_operations import registry
from ui.overlay import Overlay
from domains.screen import ScreenCapture
from domains.computer_vision_workflows import WorkflowEngine

# Load environment variables from .env file
load_dotenv()

# App Class
class App:
    def __init__(self):
        self.screen = ScreenCapture()
        self.overlay = Overlay()
        self.workflow_engine = WorkflowEngine(registry, self.screen)
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
        self.overlay.register_workflow_engine(self.workflow_engine)
        self.overlay.capture_target_callback = self.screen.set_capture_target
        self.loop.run_in_executor(self.executor, self.screen.start)  # start screen capture in another thread
        self.loop.run_in_executor(self.executor, self.overlay.show)  # start GTK in another thread

        self.loop.run_forever()

# Run the App
if __name__ == "__main__":
    app = App()
    app.run()