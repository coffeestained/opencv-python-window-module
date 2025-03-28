import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pynput import keyboard
from utils.logging import logger
from ui.overlay import Overlay

# Load environment variables from .env file
load_dotenv()

# Thread pool executor
executor = ThreadPoolExecutor()

# Listens for a escape key release and then closes the program
def on_release(key):
    logger.info(f"Key released: {key}")
    if key == keyboard.Key.esc:
        logger.info("Program terminated by user.")
        os._exit(0)

# Run the App
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    
    # Loop Run Until Complete Items
    overlay = Overlay(target_window_name=os.getenv("TARGET_WINDOW_NAME"))
    listener = keyboard.Listener(
        on_release=on_release)
    
    # Run the loop
    loop.run_until_complete(asyncio.gather(
        listener.start(),
        overlay.show(),
    ))