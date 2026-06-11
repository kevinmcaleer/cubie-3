"""Depth perception safety layer.

Monocular depth estimation with Depth Anything V2 (small) running through
ONNX Runtime on the Pi 5's CPU. This layer never navigates — it only vetoes:
Claude decides where to go, the depth map decides whether it's safe to.

Get the model (one-off, on the Pi):
    wget https://github.com/fabio-sim/Depth-Anything-ONNX/releases/latest/download/depth_anything_v2_vits.onnx \
         -O models/depth_anything_v2_vits.onnx
"""

import cv2
import numpy as np
import onnxruntime as ort

# Depth Anything V2 input size and ImageNet normalisation
INPUT_SIZE = 518
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


class DepthEstimator:
    def __init__(self, model_path="models/depth_anything_v2_vits.onnx"):
        self._session = ort.InferenceSession(
            model_path, providers=["CPUExecutionProvider"]
        )
        self._input_name = self._session.get_inputs()[0].name

    def estimate(self, rgb_frame):
        """Return a relative depth map normalised to 0..1, where 1 = closest.

        Depth Anything outputs inverse relative depth (bigger = closer) with
        no absolute scale, so we normalise per-frame. Good enough for a veto
        layer; thresholds are calibrated empirically.
        """
        h, w = rgb_frame.shape[:2]
        img = cv2.resize(rgb_frame, (INPUT_SIZE, INPUT_SIZE)).astype(np.float32) / 255.0
        img = (img - MEAN) / STD
        img = np.transpose(img, (2, 0, 1))[np.newaxis]  # NCHW

        depth = self._session.run(None, {self._input_name: img})[0].squeeze()
        depth = cv2.resize(depth, (w, h))
        lo, hi = depth.min(), depth.max()
        return (depth - lo) / (hi - lo + 1e-6)


class ObstacleGuard:
    """Checks the robot's path for anything too close to drive into.

    Looks at the bottom-centre of the depth map — the patch of world directly
    ahead of the wheels — and vetoes if too much of it is "near".
    """

    def __init__(self, estimator, near_threshold=0.82, blocked_fraction=0.18):
        self.estimator = estimator
        self.near_threshold = near_threshold      # 0..1 depth value that counts as "near"
        self.blocked_fraction = blocked_fraction  # how much of the ROI may be near before we veto

    def path_roi(self, depth_map):
        h, w = depth_map.shape
        return depth_map[int(h * 0.55):, int(w * 0.25):int(w * 0.75)]

    def is_path_clear(self, rgb_frame):
        depth = self.estimator.estimate(rgb_frame)
        roi = self.path_roi(depth)
        near = float((roi > self.near_threshold).mean())
        return near < self.blocked_fraction, near

    def debug_view(self, rgb_frame):
        """Side-by-side camera + depth map image — the screen-capture shot for the video."""
        depth = self.estimator.estimate(rgb_frame)
        depth_vis = cv2.applyColorMap((depth * 255).astype(np.uint8), cv2.COLORMAP_INFERNO)
        depth_vis = cv2.cvtColor(depth_vis, cv2.COLOR_BGR2RGB)
        return np.hstack([rgb_frame, depth_vis])
