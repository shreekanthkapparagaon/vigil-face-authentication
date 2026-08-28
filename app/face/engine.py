from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass(frozen=True)
class FaceDetection:
    """Information about a detected face."""

    x: int
    y: int
    width: int
    height: int
    confidence: float = 1.0
    landmarks: tuple[float, ...] = ()

    @property
    def box(self) -> tuple[int, int, int, int]:
        """Return the face rectangle as x, y, width, height."""
        return self.x, self.y, self.width, self.height


@dataclass(frozen=True)
class FaceMatch:
    """Result of comparing an input embedding with stored embeddings."""

    index: int
    similarity: float


class FaceEngine:
    """
    Face detection and recognition engine.

    Uses OpenCV YuNet for face detection and SFace for
    face recognition.

    This class contains no database or UI logic.
    """

    EMBEDDING_SIZE = 128
    RECOGNITION_SIZE = (112, 112)

    def __init__(
        self,
        detection_scale: float = 0.75,
        min_face_size: tuple[int, int] = (60, 60),
        detector_model_path: str | Path | None = None,
        recognition_model_path: str | Path | None = None,
    ) -> None:
        self.detection_scale = min(
            max(detection_scale, 0.25),
            1.0,
        )

        self.min_face_size = min_face_size

        self._detector_model_path = (
            Path(detector_model_path)
            if detector_model_path is not None
            else self._default_detector_model_path()
        )

        self._recognition_model_path = (
            Path(recognition_model_path)
            if recognition_model_path is not None
            else self._default_recognition_model_path()
        )

        self._detector = self._load_detector()
        self._recognizer = self._load_recognizer()

    # -----------------------------------------------------
    # Model loading
    # -----------------------------------------------------

    @staticmethod
    def _default_detector_model_path() -> Path:
        """Return the default YuNet model path."""
        return (
            Path(__file__).resolve().parents[2]
            / "data"
            / "face_detection_yunet_2023mar.onnx"
        )

    @staticmethod
    def _default_recognition_model_path() -> Path:
        """Return the default SFace model path."""
        return (
            Path(__file__).resolve().parents[2]
            / "data"
            / "face_recognition_sface_2021dec.onnx"
        )

    def _load_detector(self):
        """Load the YuNet face detector."""
        if not self._detector_model_path.exists():
            raise FileNotFoundError(
                "YuNet face detection model was not found: "
                f"{self._detector_model_path}"
            )

        detector = cv2.FaceDetectorYN.create(
            str(self._detector_model_path),
            "",
            (320, 320),
            0.65,
            0.3,
            5000,
        )

        if detector is None:
            raise RuntimeError(
                "Failed to initialize the YuNet face detector."
            )

        return detector

    def _load_recognizer(self):
        """Load the SFace face-recognition model."""
        if not self._recognition_model_path.exists():
            raise FileNotFoundError(
                "SFace recognition model was not found: "
                f"{self._recognition_model_path}"
            )

        recognizer = cv2.FaceRecognizerSF.create(
            str(self._recognition_model_path),
            "",
        )

        if recognizer is None:
            raise RuntimeError(
                "Failed to initialize the SFace recognizer."
            )

        return recognizer

    # -----------------------------------------------------
    # Face detection
    # -----------------------------------------------------

    def detect_faces(
        self,
        frame: np.ndarray,
    ) -> list[FaceDetection]:
        """
        Detect faces in a BGR camera frame.

        YuNet returns a 15-value detection containing:

        x, y, width, height,
        right-eye,
        left-eye,
        nose,
        right-mouth,
        left-mouth,
        confidence.

        Coordinates are converted back to the original
        camera-frame coordinate system.
        """
        self._validate_frame(frame)

        if frame.ndim == 2:
            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_GRAY2BGR,
            )

        frame_height, frame_width = frame.shape[:2]

        scale = self.detection_scale

        if scale < 1.0:
            detection_frame = cv2.resize(
                frame,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_AREA,
            )
        else:
            detection_frame = frame

        detection_height, detection_width = (
            detection_frame.shape[:2]
        )

        self._detector.setInputSize(
            (
                detection_width,
                detection_height,
            )
        )

        _, faces = self._detector.detect(
            detection_frame
        )

        if faces is None:
            return []

        inverse_scale = 1.0 / scale

        minimum_width = self.min_face_size[0]
        minimum_height = self.min_face_size[1]

        detections: list[FaceDetection] = []

        for face in faces:
            if len(face) < 15:
                continue

            detected_x = float(face[0])
            detected_y = float(face[1])
            detected_width = float(face[2])
            detected_height = float(face[3])
            confidence = float(face[14])

            width = int(
                round(
                    detected_width
                    * inverse_scale
                )
            )

            height = int(
                round(
                    detected_height
                    * inverse_scale
                )
            )

            if (
                width < minimum_width
                or height < minimum_height
            ):
                continue

            x = int(
                round(
                    detected_x
                    * inverse_scale
                )
            )

            y = int(
                round(
                    detected_y
                    * inverse_scale
                )
            )

            # -------------------------------------------------
            # Clamp against the ACTUAL FRAME dimensions.
            #
            # This is the important fix for the previous
            # bounding-box positioning bug.
            # -------------------------------------------------

            x = max(
                0,
                min(
                    x,
                    frame_width - 1,
                ),
            )

            y = max(
                0,
                min(
                    y,
                    frame_height - 1,
                ),
            )

            right = min(
                frame_width,
                x + width,
            )

            bottom = min(
                frame_height,
                y + height,
            )

            width = right - x
            height = bottom - y

            if width <= 0 or height <= 0:
                continue

            # -------------------------------------------------
            # Convert YuNet's five landmarks back to the
            # original camera-frame coordinate system.
            # -------------------------------------------------

            landmarks: list[float] = []

            for index in range(4, 14):
                landmarks.append(
                    float(face[index])
                    * inverse_scale
                )

            detections.append(
                FaceDetection(
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    confidence=confidence,
                    landmarks=tuple(landmarks),
                )
            )

        detections.sort(
            key=lambda detection: (
                detection.width
                * detection.height
            ),
            reverse=True,
        )

        return detections

    # -----------------------------------------------------
    # Face crop
    # -----------------------------------------------------

    def crop_face(
        self,
        frame: np.ndarray,
        detection: FaceDetection,
        padding: float = 0.20,
    ) -> np.ndarray | None:
        """Crop a detected face with optional padding."""
        self._validate_frame(frame)

        frame_height, frame_width = (
            frame.shape[:2]
        )

        x, y, width, height = detection.box

        if width <= 0 or height <= 0:
            return None

        pad_x = int(width * padding)
        pad_y = int(height * padding)

        left = max(
            0,
            x - pad_x,
        )

        top = max(
            0,
            y - pad_y,
        )

        right = min(
            frame_width,
            x + width + pad_x,
        )

        bottom = min(
            frame_height,
            y + height + pad_y,
        )

        if right <= left or bottom <= top:
            return None

        return frame[
            top:bottom,
            left:right,
        ].copy()

    # -----------------------------------------------------
    # Face alignment
    # -----------------------------------------------------

    def align_face(
        self,
        frame: np.ndarray,
        detection: FaceDetection,
    ) -> np.ndarray | None:
        """
        Align a detected face using YuNet's five landmarks.

        SFace is designed to receive an aligned 112x112 face.
        """
        self._validate_frame(frame)

        if len(detection.landmarks) != 10:
            return self.crop_face(
                frame,
                detection,
                padding=0.20,
            )

        face_data = np.array(
            [
                *detection.box,
                *detection.landmarks,
                detection.confidence,
            ],
            dtype=np.float32,
        )

        try:
            aligned = self._recognizer.alignCrop(
                frame,
                face_data,
            )
        except cv2.error:
            return self.crop_face(
                frame,
                detection,
                padding=0.20,
            )

        if aligned is None or aligned.size == 0:
            return None

        return aligned

    # -----------------------------------------------------
    # Face embedding
    # -----------------------------------------------------

    def generate_embedding(
        self,
        face: np.ndarray,
    ) -> np.ndarray:
        """
        Generate a normalized SFace embedding.

        The supplied image should preferably already be
        aligned using align_face().
        """
        if face is None or face.size == 0:
            raise ValueError(
                "Face image cannot be empty."
            )

        if face.ndim == 2:
            face = cv2.cvtColor(
                face,
                cv2.COLOR_GRAY2BGR,
            )

        if face.ndim != 3 or face.shape[2] != 3:
            raise ValueError(
                "Face image must be a BGR image."
            )

        height, width = face.shape[:2]

        if width < 20 or height < 20:
            raise ValueError(
                "Face image is too small."
            )

        if (
            width != self.RECOGNITION_SIZE[0]
            or height != self.RECOGNITION_SIZE[1]
        ):
            face = cv2.resize(
                face,
                self.RECOGNITION_SIZE,
                interpolation=cv2.INTER_AREA,
            )

        embedding = self._recognizer.feature(
            face
        )

        if embedding is None:
            raise ValueError(
                "Unable to generate a face embedding."
            )

        embedding = np.asarray(
            embedding,
            dtype=np.float32,
        ).reshape(-1)

        if embedding.size == 0:
            raise ValueError(
                "Generated face embedding is empty."
            )

        if embedding.size != self.EMBEDDING_SIZE:
            raise ValueError(
                "SFace returned an unexpected embedding "
                f"dimension: {embedding.size}"
            )

        return self._normalize_embedding(
            embedding
        )

    def embedding_from_frame(
        self,
        frame: np.ndarray,
        detection: FaceDetection | None = None,
    ) -> np.ndarray | None:
        """
        Detect a face and generate an aligned SFace embedding.
        """
        self._validate_frame(frame)

        if detection is None:
            detections = self.detect_faces(
                frame
            )

            if not detections:
                return None

            detection = self.select_largest_face(
                detections
            )

        aligned_face = self.align_face(
            frame,
            detection,
        )

        if aligned_face is None:
            return None

        return self.generate_embedding(
            aligned_face
        )

    # -----------------------------------------------------
    # Enrollment profile
    # -----------------------------------------------------

    def build_face_profile(
        self,
        embeddings: list[np.ndarray],
    ) -> np.ndarray:
        """
        Build a stable user profile from multiple embeddings.

        Multiple enrollment samples are averaged and the
        resulting vector is normalized again.
        """
        if not embeddings:
            raise ValueError(
                "At least one embedding is required."
            )

        normalized_embeddings: list[np.ndarray] = []

        for embedding in embeddings:
            normalized_embeddings.append(
                self._normalize_embedding(
                    embedding
                )
            )

        matrix = np.vstack(
            normalized_embeddings
        )

        profile = np.mean(
            matrix,
            axis=0,
            dtype=np.float32,
        )

        return self._normalize_embedding(
            profile
        )

    # -----------------------------------------------------
    # Face selection
    # -----------------------------------------------------

    @staticmethod
    def select_largest_face(
        detections: list[FaceDetection],
    ) -> FaceDetection:
        """Return the largest detected face."""
        if not detections:
            raise ValueError(
                "No face detections available."
            )

        return max(
            detections,
            key=lambda detection: (
                detection.width
                * detection.height
            ),
        )

    # -----------------------------------------------------
    # Embedding comparison
    # -----------------------------------------------------

    @staticmethod
    def cosine_similarity(
        embedding_a: np.ndarray,
        embedding_b: np.ndarray,
    ) -> float:
        """Calculate cosine similarity between embeddings."""
        a = np.asarray(
            embedding_a,
            dtype=np.float32,
        ).reshape(-1)

        b = np.asarray(
            embedding_b,
            dtype=np.float32,
        ).reshape(-1)

        if a.size == 0 or b.size == 0:
            raise ValueError(
                "Embeddings cannot be empty."
            )

        if a.shape != b.shape:
            raise ValueError(
                "Embeddings must have the same dimension."
            )

        a_norm = np.linalg.norm(a)
        b_norm = np.linalg.norm(b)

        if (
            a_norm <= 1e-8
            or b_norm <= 1e-8
        ):
            return 0.0

        similarity = float(
            np.dot(a, b)
            / (a_norm * b_norm)
        )

        return float(
            np.clip(
                similarity,
                -1.0,
                1.0,
            )
        )

    def find_best_match(
        self,
        query_embedding: np.ndarray,
        stored_embeddings: list[np.ndarray],
        threshold: float = 0.363,
    ) -> FaceMatch | None:
        """
        Find the highest-similarity stored face profile.
        """
        if not stored_embeddings:
            return None

        query = self._normalize_embedding(
            query_embedding
        )

        matrix = np.asarray(
            stored_embeddings,
            dtype=np.float32,
        )

        if matrix.ndim != 2:
            raise ValueError(
                "Stored embeddings must form a 2D matrix."
            )

        if matrix.shape[1] != query.size:
            raise ValueError(
                "Stored embeddings have incompatible dimensions."
            )

        matrix_norms = np.linalg.norm(
            matrix,
            axis=1,
        )

        valid_rows = (
            matrix_norms > 1e-8
        )

        if not np.any(valid_rows):
            return None

        normalized_matrix = np.zeros_like(
            matrix,
            dtype=np.float32,
        )

        normalized_matrix[
            valid_rows
        ] = (
            matrix[valid_rows]
            / matrix_norms[
                valid_rows,
                None,
            ]
        )

        similarities = np.full(
            matrix.shape[0],
            -1.0,
            dtype=np.float32,
        )

        similarities[
            valid_rows
        ] = (
            normalized_matrix[
                valid_rows
            ]
            @ query
        )

        best_index = int(
            np.argmax(
                similarities
            )
        )

        best_similarity = float(
            similarities[
                best_index
            ]
        )

        if best_similarity < threshold:
            return None

        return FaceMatch(
            index=best_index,
            similarity=best_similarity,
        )

    # -----------------------------------------------------
    # Validation / normalization
    # -----------------------------------------------------

    @staticmethod
    def _normalize_embedding(
        embedding: np.ndarray,
    ) -> np.ndarray:
        """Return a float32 unit-length embedding."""
        vector = np.asarray(
            embedding,
            dtype=np.float32,
        ).reshape(-1)

        if vector.size == 0:
            raise ValueError(
                "Embedding cannot be empty."
            )

        norm = np.linalg.norm(
            vector
        )

        if norm <= 1e-8:
            raise ValueError(
                "Embedding cannot be normalized."
            )

        return (
            vector / norm
        ).astype(
            np.float32
        )

    @staticmethod
    def _validate_frame(
        frame: np.ndarray,
    ) -> None:
        """Validate a camera frame."""
        if not isinstance(
            frame,
            np.ndarray,
        ):
            raise TypeError(
                "Frame must be a NumPy array."
            )

        if frame.size == 0:
            raise ValueError(
                "Frame cannot be empty."
            )

        if frame.ndim not in (
            2,
            3,
        ):
            raise ValueError(
                "Frame must be a 2D or 3D NumPy array."
            )

        if frame.ndim == 3 and frame.shape[2] not in (
            1,
            3,
            4,
        ):
            raise ValueError(
                "Frame must have 1, 3, or 4 channels."
            )
