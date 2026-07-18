# modules/camera_manager.py
# Handles camera capture, including disconnect detection and reconnect attempts.

import cv2
import time

class CameraManager:
    def __init__(self, camera_index=0, width=640, height=480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        self._open_camera()

    def _open_camera(self):
        """Attempt to open the camera."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if self.width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        if not self.cap.isOpened():
            print("[CameraManager] ERROR: Could not open camera.")
            return False
        print("[CameraManager] Camera opened successfully.")
        return True

    def get_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return False, None
        ret, frame = self.cap.read()
        if not ret:
            print("[CameraManager] WARNING: Frame read failed. Attempting reconnect...")
            return self._attempt_reconnect()
        return True, frame

    def _attempt_reconnect(self, retries=3, delay=1.0):
        """Try to reopen the camera a few times before giving up."""
        for attempt in range(1, retries + 1):
            print(f"[CameraManager] Reconnect attempt {attempt}/{retries}...")
            self.release()
            time.sleep(delay)
            if self._open_camera():
                ret, frame = self.cap.read()
                if ret:
                    print("[CameraManager] Reconnect successful.")
                    return True, frame
        print("[CameraManager] ERROR: Camera disconnected and could not reconnect.")
        return False, None

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

# ---------- Standalone test ----------
if __name__ == "__main__":
    cam = CameraManager(camera_index=0)
    print("Press 'q' to quit test window.")
    while True:
        success, frame = cam.get_frame()
        if not success:
            print("Camera failed permanently. Exiting test.")
            break
        cv2.imshow("Camera Test - VISION", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
