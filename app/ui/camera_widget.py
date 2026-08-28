from __future__ import annotations

import time

import cv2
import numpy as np

from PyQt6.QtCore import (
    QMutex,
    QMutexLocker,
    QThread,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.face.engine import FaceDetection, FaceEngine


class CameraWorker(QThread):
    """Background camera capture worker."""

    frame_ready = pyqtSignal(object)
    camera_error = pyqtSignal(str)

    def __init__(
        self,
        camera_index: int = 0,
    ) -> None:
        super().__init__()

        self.camera_index = camera_index
        self._running = False

    def run(self) -> None:
        """Open and continuously capture camera frames."""

        capture = None

        try:
            # -------------------------------------------------
            # Try DirectShow first on Windows.
            # -------------------------------------------------
            capture = cv2.VideoCapture(
                self.camera_index,
                cv2.CAP_DSHOW,
            )

            # -------------------------------------------------
            # Fall back to OpenCV default backend.
            # -------------------------------------------------
            if not capture.isOpened():
                capture.release()

                capture = cv2.VideoCapture(
                    self.camera_index
                )

            if not capture.isOpened():
                self.camera_error.emit(
                    "Unable to open camera."
                )
                return

            # -------------------------------------------------
            # Camera properties can fail on some webcams.
            # Never allow that to kill the worker.
            # -------------------------------------------------
            self._safe_set(
                capture,
                cv2.CAP_PROP_FRAME_WIDTH,
                1280,
            )

            self._safe_set(
                capture,
                cv2.CAP_PROP_FRAME_HEIGHT,
                720,
            )

            self._safe_set(
                capture,
                cv2.CAP_PROP_FPS,
                30,
            )

            self._running = True

            while (
                self._running
                and not self.isInterruptionRequested()
            ):
                success, frame = capture.read()

                if not success or frame is None:
                    self.camera_error.emit(
                        "Unable to read camera frame."
                    )
                    break

                self.frame_ready.emit(frame)

                self.msleep(25)

        except Exception as exc:
            self.camera_error.emit(
                f"Camera error: {exc}"
            )

        finally:
            self._running = False

            if capture is not None:
                try:
                    capture.release()
                except Exception:
                    pass

    @staticmethod
    def _safe_set(
        capture,
        property_id: int,
        value: float,
    ) -> None:
        """Safely set a camera property."""
        try:
            capture.set(
                property_id,
                value,
            )
        except Exception:
            pass

    def stop(self) -> None:
        """Request worker shutdown."""
        self._running = False
        self.requestInterruption()


class CameraWidget(QWidget):
    """
    Futuristic camera preview.

    Handles:
    - camera capture
    - face detection
    - futuristic overlays
    - thread lifecycle
    - latest frame storage
    """

    frame_captured = pyqtSignal(object)
    face_detected = pyqtSignal(object)

    def __init__(
        self,
        face_engine: FaceEngine | None = None,
        camera_index: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.face_engine = (
            face_engine
            or FaceEngine()
        )

        self.camera_index = camera_index

        self.worker: CameraWorker | None = None

        self._latest_frame: np.ndarray | None = None

        self._last_detections: list[
            FaceDetection
        ] = []

        self._camera_running = False
        self._restart_pending = False

        self._frame_mutex = QMutex()

        self._last_detection_time = 0.0

        self._setup_ui()

    # =====================================================
    # UI
    # =====================================================

    def _setup_ui(self) -> None:
        """Build the camera interface."""

        outer_layout = QVBoxLayout(self)

        outer_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        outer_layout.setSpacing(10)

        camera_frame = QFrame()

        camera_frame.setObjectName(
            "cameraFrame"
        )

        camera_layout = QVBoxLayout(
            camera_frame
        )

        camera_layout.setContentsMargins(
            14,
            14,
            14,
            14,
        )

        camera_layout.setSpacing(10)

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        header_layout = QHBoxLayout()

        camera_title = QLabel(
            "VISION SENSOR"
        )

        camera_title.setObjectName(
            "cameraTitle"
        )

        self.signal_label = QLabel(
            "● STANDBY"
        )

        self.signal_label.setObjectName(
            "cameraSignal"
        )

        header_layout.addWidget(
            camera_title
        )

        header_layout.addStretch()

        header_layout.addWidget(
            self.signal_label
        )

        camera_layout.addLayout(
            header_layout
        )

        # -------------------------------------------------
        # Preview
        # -------------------------------------------------

        self.preview = QLabel()

        self.preview.setObjectName(
            "cameraPreview"
        )

        self.preview.setMinimumSize(
            640,
            420,
        )

        self.preview.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.preview.setText(
            "CAMERA OFFLINE"
        )

        camera_layout.addWidget(
            self.preview,
            stretch=1,
        )

        # -------------------------------------------------
        # Status
        # -------------------------------------------------

        status_layout = QHBoxLayout()

        self.camera_status = QLabel(
            "● Camera offline"
        )

        self.camera_status.setObjectName(
            "cameraStatus"
        )

        self.face_status = QLabel(
            "NO SUBJECT"
        )

        self.face_status.setObjectName(
            "faceStatus"
        )

        status_layout.addWidget(
            self.camera_status
        )

        status_layout.addStretch()

        status_layout.addWidget(
            self.face_status
        )

        camera_layout.addLayout(
            status_layout
        )

        outer_layout.addWidget(
            camera_frame,
            stretch=1,
        )

    # =====================================================
    # Camera lifecycle
    # =====================================================

    def start_camera(self) -> None:
        """Start camera safely."""

        # Already running.
        if (
            self.worker is not None
            and self.worker.isRunning()
        ):
            self._camera_running = True
            return

        # Previous worker is shutting down.
        if (
            self.worker is not None
            and not self.worker.isFinished()
        ):
            self._restart_pending = True
            return

        self._restart_pending = False

        self.worker = CameraWorker(
            camera_index=self.camera_index
        )

        self.worker.frame_ready.connect(
            self._on_frame
        )

        self.worker.camera_error.connect(
            self._on_camera_error
        )

        self.worker.finished.connect(
            self._on_worker_finished
        )

        self._camera_running = True

        self.camera_status.setText(
            "● Initializing vision sensor..."
        )

        self.signal_label.setText(
            "● CONNECTING"
        )

        self.preview.setText(
            "INITIALIZING CAMERA..."
        )

        self.worker.start()

    def stop_camera(self) -> None:
        """Request camera shutdown without destroying a running QThread."""

        self._camera_running = False

        worker = self.worker

        if worker is None:
            self._set_offline_state()
            return

        if worker.isRunning():
            worker.stop()

            self.camera_status.setText(
                "● Releasing camera..."
            )

            self.signal_label.setText(
                "● DISCONNECTING"
            )

            return

        self._cleanup_worker()

        self._set_offline_state()

    def _on_worker_finished(self) -> None:
        """Handle camera worker completion."""

        self._cleanup_worker()

        self._set_offline_state()

        if self._restart_pending:
            self._restart_pending = False

            # Start again only after the old thread is fully finished.
            self.start_camera()

    def _cleanup_worker(self) -> None:
        """Safely release the completed worker."""

        worker = self.worker

        if worker is None:
            return

        if worker.isRunning():
            return

        try:
            worker.deleteLater()
        except RuntimeError:
            pass

        self.worker = None

    def _set_offline_state(self) -> None:
        """Reset camera UI."""

        self.camera_status.setText(
            "● Camera offline"
        )

        self.signal_label.setText(
            "● STANDBY"
        )

        self.face_status.setText(
            "NO SUBJECT"
        )

        if not self._camera_running:
            self.preview.clear()
            self.preview.setText(
                "CAMERA OFFLINE"
            )

    # =====================================================
    # Frame processing
    # =====================================================

    def _on_frame(
        self,
        frame: np.ndarray,
    ) -> None:
        """Process a camera frame."""

        if frame is None or frame.size == 0:
            return

        with QMutexLocker(
            self._frame_mutex
        ):
            self._latest_frame = frame.copy()

        detections: list[
            FaceDetection
        ] = []

        try:
            detections = (
                self.face_engine.detect_faces(
                    frame
                )
            )

        except Exception as exc:
            self.face_status.setText(
                "DETECTION ERROR"
            )

            self.camera_status.setText(
                f"● {exc}"
            )

        self._last_detections = detections

        if detections:
            self.face_status.setText(
                f"{len(detections)} "
                + (
                    "SUBJECT"
                    if len(detections) == 1
                    else "SUBJECTS"
                )
            )

            self.signal_label.setText(
                "● FACE LOCK"
            )

            self.camera_status.setText(
                "● Vision system active"
            )

            self.face_detected.emit(
                detections
            )

        else:
            self.face_status.setText(
                "NO SUBJECT"
            )

            self.signal_label.setText(
                "● SCANNING"
            )

            self.camera_status.setText(
                "● Searching for face..."
            )

        display_frame = self._draw_detections(
            frame.copy(),
            detections,
        )

        self._display_frame(
            display_frame
        )

        self.frame_captured.emit(
            frame.copy()
        )

    # =====================================================
    # Futuristic face overlay
    # =====================================================

    def _draw_detections(
        self,
        frame: np.ndarray,
        detections: list[FaceDetection],
    ) -> np.ndarray:
        """Draw futuristic face tracking graphics."""

        height, width = frame.shape[:2]

        # -------------------------------------------------
        # Global HUD corners.
        # -------------------------------------------------

        hud_color = (0, 210, 255)

        corner_size = 35

        cv2.line(
            frame,
            (20, 20),
            (20 + corner_size, 20),
            hud_color,
            2,
        )

        cv2.line(
            frame,
            (20, 20),
            (20, 20 + corner_size),
            hud_color,
            2,
        )

        cv2.line(
            frame,
            (width - 20, 20),
            (width - 20 - corner_size, 20),
            hud_color,
            2,
        )

        cv2.line(
            frame,
            (width - 20, 20),
            (width - 20, 20 + corner_size),
            hud_color,
            2,
        )

        cv2.line(
            frame,
            (20, height - 20),
            (20 + corner_size, height - 20),
            hud_color,
            2,
        )

        cv2.line(
            frame,
            (20, height - 20),
            (20, height - 20 - corner_size),
            hud_color,
            2,
        )

        cv2.line(
            frame,
            (width - 20, height - 20),
            (width - 20 - corner_size, height - 20),
            hud_color,
            2,
        )

        cv2.line(
            frame,
            (width - 20, height - 20),
            (width - 20, height - 20 - corner_size),
            hud_color,
            2,
        )

        # -------------------------------------------------
        # Face detections.
        # -------------------------------------------------

        for detection in detections:
            x, y, box_width, box_height = (
                detection.box
            )

            right = min(
                width - 1,
                x + box_width,
            )

            bottom = min(
                height - 1,
                y + box_height,
            )

            x = max(0, x)
            y = max(0, y)

            # Thin bounding rectangle.
            cv2.rectangle(
                frame,
                (x, y),
                (right, bottom),
                (0, 210, 255),
                1,
            )

            corner = max(
                18,
                min(
                    box_width,
                    box_height,
                )
                // 5,
            )

            line_width = 3

            # Top-left.
            cv2.line(
                frame,
                (x, y),
                (x + corner, y),
                (0, 255, 255),
                line_width,
            )

            cv2.line(
                frame,
                (x, y),
                (x, y + corner),
                (0, 255, 255),
                line_width,
            )

            # Top-right.
            cv2.line(
                frame,
                (right, y),
                (right - corner, y),
                (0, 255, 255),
                line_width,
            )

            cv2.line(
                frame,
                (right, y),
                (right, y + corner),
                (0, 255, 255),
                line_width,
            )

            # Bottom-left.
            cv2.line(
                frame,
                (x, bottom),
                (x + corner, bottom),
                (0, 255, 255),
                line_width,
            )

            cv2.line(
                frame,
                (x, bottom),
                (x, bottom - corner),
                (0, 255, 255),
                line_width,
            )

            # Bottom-right.
            cv2.line(
                frame,
                (right, bottom),
                (right - corner, bottom),
                (0, 255, 255),
                line_width,
            )

            cv2.line(
                frame,
                (right, bottom),
                (right, bottom - corner),
                (0, 255, 255),
                line_width,
            )

            # -------------------------------------------------
            # Center targeting reticle.
            # -------------------------------------------------

            center_x = x + box_width // 2
            center_y = y + box_height // 2

            reticle = 10

            cv2.line(
                frame,
                (
                    center_x - reticle,
                    center_y,
                ),
                (
                    center_x + reticle,
                    center_y,
                ),
                (0, 220, 255),
                1,
            )

            cv2.line(
                frame,
                (
                    center_x,
                    center_y - reticle,
                ),
                (
                    center_x,
                    center_y + reticle,
                ),
                (0, 220, 255),
                1,
            )

            # -------------------------------------------------
            # Face information.
            # -------------------------------------------------

            confidence_text = (
                f"FACE // "
                f"{detection.confidence:.0%}"
            )

            text_y = max(
                25,
                y - 10,
            )

            cv2.putText(
                frame,
                confidence_text,
                (
                    x,
                    text_y,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (0, 230, 255),
                1,
                cv2.LINE_AA,
            )

        # -------------------------------------------------
        # Bottom HUD.
        # -------------------------------------------------

        cv2.putText(
            frame,
            "NEURAL VISION // ONLINE",
            (
                24,
                height - 28,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (150, 220, 230),
            1,
            cv2.LINE_AA,
        )

        return frame

    # =====================================================
    # Display
    # =====================================================

    def _display_frame(
        self,
        frame: np.ndarray,
    ) -> None:
        """Convert OpenCV frame to a Qt pixmap."""

        if frame is None or frame.size == 0:
            return

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        height, width, channels = (
            rgb_frame.shape
        )

        bytes_per_line = (
            channels * width
        )

        image = QImage(
            rgb_frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888,
        ).copy()

        pixmap = QPixmap.fromImage(
            image
        )

        scaled_pixmap = pixmap.scaled(
            self.preview.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.preview.setPixmap(
            scaled_pixmap
        )

    # =====================================================
    # Errors
    # =====================================================

    def _on_camera_error(
        self,
        message: str,
    ) -> None:
        """Handle camera errors."""

        self._camera_running = False

        self.camera_status.setText(
            f"● {message}"
        )

        self.signal_label.setText(
            "● ERROR"
        )

        self.face_status.setText(
            "CAMERA ERROR"
        )

        self.preview.clear()

        self.preview.setText(
            message
        )

    # =====================================================
    # Public helpers
    # =====================================================

    def get_latest_frame(
        self,
    ) -> np.ndarray | None:
        """Return a copy of the latest frame."""

        with QMutexLocker(
            self._frame_mutex
        ):
            if self._latest_frame is None:
                return None

            return self._latest_frame.copy()

    def get_latest_detections(
        self,
    ) -> list[FaceDetection]:
        """Return latest face detections."""

        return list(
            self._last_detections
        )

    def capture_frame(
        self,
    ) -> np.ndarray | None:
        """Return current camera frame."""

        return self.get_latest_frame()

    # =====================================================
    # Cleanup
    # =====================================================

    def closeEvent(
        self,
        event,
    ) -> None:
        """Stop camera before widget destruction."""

        self.stop_camera()

        # Do not wait indefinitely here.
        event.accept()