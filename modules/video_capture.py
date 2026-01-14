import cv2
import numpy as np
from typing import Optional, Tuple, Callable
import platform
import threading
import sys
import subprocess

# Only import Windows-specific library if on Windows
if platform.system() == "Windows":
    from pygrabber.dshow_graph import FilterGraph


class VideoCapturer:
    def __init__(self, device_index: int):
        self.device_index = device_index
        self.frame_callback = None
        self._current_frame = None
        self._frame_ready = threading.Event()
        self.is_running = False
        self.cap = None

        # Initialize Windows-specific components if on Windows
        if platform.system() == "Windows":
            self.graph = FilterGraph()
            # Verify device exists
            devices = self.graph.get_input_devices()
            if self.device_index >= len(devices):
                raise ValueError(
                    f"Invalid device index {device_index}. Available devices: {len(devices)}"
                )

    def start(self, width: int = 960, height: int = 540, fps: int = 60) -> bool:
        """Initialize and start video capture"""
        try:
            # Handle macOS camera permissions
            if platform.system() == "Darwin":
                if not self._check_macos_camera_permission():
                    print("\n" + "="*70)
                    print("CAMERA PERMISSION REQUIRED")
                    print("="*70)
                    print("\nOpenCV needs camera access but doesn't have permission.")
                    print("\nTo fix this issue:")
                    print("\n1. Go to System Settings > Privacy & Security > Camera")
                    print("2. Enable camera access for your Terminal app")
                    print("   (e.g., Terminal.app, iTerm.app, or your Python executable)")
                    print("\n3. If you don't see your terminal in the list:")
                    print("   - Close this application")
                    print("   - Run this command to reset permissions:")
                    print("     tccutil reset Camera")
                    print("   - Restart the application")
                    print("\n4. Alternatively, run Python from an app bundle that has permissions")
                    print("\n" + "="*70)
                    return False
                    
            if platform.system() == "Windows":
                # Windows-specific capture methods
                capture_methods = [
                    (self.device_index, cv2.CAP_DSHOW),  # Try DirectShow first
                    (self.device_index, cv2.CAP_ANY),  # Then try default backend
                    (-1, cv2.CAP_ANY),  # Try -1 as fallback
                    (0, cv2.CAP_ANY),  # Finally try 0 without specific backend
                ]

                for dev_id, backend in capture_methods:
                    try:
                        self.cap = cv2.VideoCapture(dev_id, backend)
                        if self.cap.isOpened():
                            break
                        self.cap.release()
                    except Exception:
                        continue
            elif platform.system() == "Darwin":
                # macOS-specific capture with AVFoundation backend
                # Try AVFoundation explicitly first
                try:
                    self.cap = cv2.VideoCapture(self.device_index, cv2.CAP_AVFOUNDATION)
                    if not self.cap.isOpened():
                        self.cap.release()
                        # Fallback to default
                        self.cap = cv2.VideoCapture(self.device_index)
                except Exception:
                    self.cap = cv2.VideoCapture(self.device_index)
            else:
                # Linux capture method
                self.cap = cv2.VideoCapture(self.device_index)

            if not self.cap or not self.cap.isOpened():
                raise RuntimeError("Failed to open camera")

            # Configure format
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FPS, fps)

            self.is_running = True
            return True

        except Exception as e:
            print(f"Failed to start capture: {str(e)}")
            if self.cap:
                self.cap.release()
            return False

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a frame from the camera"""
        if not self.is_running or self.cap is None:
            return False, None

        ret, frame = self.cap.read()
        if ret:
            self._current_frame = frame
            if self.frame_callback:
                self.frame_callback(frame)
            return True, frame
        return False, None

    def release(self) -> None:
        """Stop capture and release resources"""
        if self.is_running and self.cap is not None:
            self.cap.release()
            self.is_running = False
            self.cap = None

    def set_frame_callback(self, callback: Callable[[np.ndarray], None]) -> None:
        """Set callback for frame processing"""
        self.frame_callback = callback

    def _check_macos_camera_permission(self) -> bool:
        """Check if camera permissions are granted on macOS"""
        if platform.system() != "Darwin":
            return True
            
        # Try to open camera briefly to check permission status
        test_cap = cv2.VideoCapture(self.device_index, cv2.CAP_AVFOUNDATION)
        
        # Give it a moment to initialize
        import time
        time.sleep(0.5)
        
        is_opened = test_cap.isOpened()
        test_cap.release()
        
        return is_opened
