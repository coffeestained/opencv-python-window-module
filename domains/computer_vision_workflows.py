import zipfile
import json
from utils.logging import logger
from domains.computer_vision_operations import OperationRegistry
from domains.screen import ScreenCapture

class WorkflowEngine:
    def __init__(self, operation_registry: OperationRegistry, screen: ScreenCapture):
        self.registry = operation_registry
        self.screen = screen
        self.started = None
        self.workflow = None

    def _validate_zip(self, zip_path: str):
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                if 'manifest.json' not in z.namelist():
                    logger.error("Manifest file not found in ZIP.")
                    return False
        except zipfile.BadZipFile:
            logger.error("Provided file is not a valid ZIP archive.")
            return False
        return True

    def _validate_screen_capture(self):
        frame = self.screen_capture.get_frame()
        if frame is None:
            logger.error("No frame could be retrieved from screen capture.")
            return False
        return True

    def start(self, zip_path: str):
        if self.started:
            logger.info("Workflow already running.")
            return

        logger.info(f"Attempting to start workflow from: {zip_path}")

        if not self._validate_zip(zip_path):
            logger.error("ZIP validation failed.")
            return

        if not self._validate_screen_capture():
            logger.error("Screen capture validation failed.")
            return

        #self.workflow = TODO WORKFLOW CLASS
        self.started = zip_path

        logger.info("Workflow started successfully.")

        while self.started:
            frame = self.screen_capture.get_frame()
            if frame is None:
                logger.warning("Lost frame. Skipping.")
                continue

            # self.workflow.execute([frame])

    def stop(self):
        if self.started:
            logger.info(f"Stopping workflow from: {self.started}")
        else:
            logger.info("No workflow is currently running.")
        self.started = None
        self.workflow = None
    