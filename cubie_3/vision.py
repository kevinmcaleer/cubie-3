"""Camera capture for Cubie-3.

Uses Picamera2 on the Raspberry Pi. Falls back to an OpenCV webcam when
Picamera2 isn't available, so the vision pipeline can be developed and
tested on a desktop machine.
"""

import cv2
import numpy as np

try:
    from picamera2 import Picamera2
    HAS_PICAMERA = True
except ImportError:
    HAS_PICAMERA = False


class Camera:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        if HAS_PICAMERA:
            self._cam = Picamera2()
            config = self._cam.create_still_configuration(
                main={"size": (width, height), "format": "RGB888"}
            )
            self._cam.configure(config)
            self._cam.start()
        else:
            self._cam = cv2.VideoCapture(0)
            self._cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self._cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def capture(self):
        """Capture a single frame as an RGB numpy array."""
        if HAS_PICAMERA:
            return self._cam.capture_array()
        ok, frame = self._cam.read()
        if not ok:
            raise RuntimeError("Failed to read frame from webcam")
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def capture_jpeg(self, quality=85):
        """Capture a frame and return it as JPEG bytes (for the AI pipeline)."""
        frame = self.capture()
        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        ok, buffer = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if not ok:
            raise RuntimeError("JPEG encoding failed")
        return buffer.tobytes()

    def close(self):
        if HAS_PICAMERA:
            self._cam.stop()
        else:
            self._cam.release()
