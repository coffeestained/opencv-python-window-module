import cv2
import numpy as np
from utils.logging import logger

class OperationRegistry:
    def __init__(self):
        self.registry = {}

    def register(self, name: str, operation_class):
        self.registry[name] = operation_class

    def get(self, name: str):
        if name not in self.registry:
            raise ValueError(f"Operation '{name}' is not registered.")
        return self.registry[name]
    
class BaseOperation:
    def __init__(self, step_manifest: dict, context: dict):
        self.step = step_manifest
        self.context = context

    def setup(self):
        pass

    def process(self, frame, context):
        raise NotImplementedError
    
class TrackObjectOperation(BaseOperation):
    def __init__(self, step_manifest, context):
        super().__init__(step_manifest, context)
        self.threshold = self.step.get("params", {}).get("threshold", 0.75)
        self.detector = cv2.ORB_create()
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.tracking = False
        self.keypoints = None
        self.descriptors = None
        self.prev_frame = None
        self.tracked_pts = []

        target_path = self.step["inputs"][0]
        img_bytes = context["assets"][target_path]
        img_array = np.frombuffer(img_bytes, np.uint8)
        self.target_image = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
        self.target_kp, self.target_desc = self.detector.detectAndCompute(self.target_image, None)

    def process(self, frame, context):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if not self.tracking or self.keypoints is None:
            kp, desc = self.detector.detectAndCompute(gray, None)
            matches = self.matcher.match(self.target_desc, desc)
            matches = sorted(matches, key=lambda x: x.distance)
            if len(matches) >= 10:
                src_pts = np.float32([self.target_kp[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
                self.tracked_pts = dst_pts
                self.tracking = True
                logger.debug("[TrackObject] Target re-acquired.")
            else:
                logger.debug("[TrackObject] Not enough matches. Still searching.")
                self.tracking = False
                self.tracked_pts = []
        else:
            self.tracking = False
            self.tracked_pts = [] 
            logger.debug("[TrackObject] Lost tracking. Reverting to detection.")

        if self.tracked_pts is not None and len(self.tracked_pts) > 0:
            pts = np.array(self.tracked_pts).reshape(-1, 2)
            x, y, w, h = cv2.boundingRect(pts.astype(np.int32))
            return {"bbox": (x, y, w, h), "tracking": self.tracking}
        else:
            return {"bbox": None, "tracking": False}

# TODO Move to configurable registry (maybe env or config or db or something)
registry = OperationRegistry()
registry.register("track_keypoints", TrackObjectOperation)