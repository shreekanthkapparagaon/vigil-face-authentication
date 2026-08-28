from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

import cv2
import numpy as np

from app.config import settings
from app.database.connection import get_connection
from app.face.engine import FaceDetection, FaceEngine
from app.schemas.authentication import AuthenticationResult
from app.schemas.user import UserCreate, UserListItem, UserResponse


class FaceAuthService:
    """Application service for face registration and authentication."""

    # Number of samples used to build a user's face profile.
    ENROLLMENT_SAMPLES = 10

    # Minimum similarity between consecutive enrollment samples.
    # This prevents completely different/poor frames from being used.
    ENROLLMENT_MIN_SIMILARITY = 0.45

    def __init__(
        self,
        face_engine: FaceEngine | None = None,
    ) -> None:
        self.face_engine = face_engine or FaceEngine(
            detection_scale=settings.face_detection_scale,
        )

        self._embedding_cache: list[tuple[int, np.ndarray]] = []
        self._cache_loaded = False

    # =====================================================
    # Registration
    # =====================================================

    def register_user(
        self,
        user: UserCreate,
        frame: np.ndarray,
        detection: FaceDetection | None = None,
    ) -> UserResponse:
        """
        Register a user using the supplied camera frame.

        This method creates the initial face profile from the
        supplied frame.

        For multi-frame enrollment, use register_from_samples().
        """
        embedding = self.face_engine.embedding_from_frame(
            frame,
            detection=detection,
        )

        if embedding is None:
            raise ValueError(
                "No face detected. Please position your face clearly."
            )

        profile = self.face_engine.build_face_profile(
            [embedding],
        )

        return self._create_user(
            user=user,
            embedding=profile,
        )

    def register_from_samples(
        self,
        user: UserCreate,
        frames: list[np.ndarray],
    ) -> UserResponse:
        """
        Register a user from multiple camera frames.

        Each frame is converted into an SFace embedding.
        A stable profile is then created from all valid samples.
        """
        if not frames:
            raise ValueError(
                "No enrollment frames were provided."
            )

        embeddings: list[np.ndarray] = []

        for frame in frames:
            embedding = self.face_engine.embedding_from_frame(
                frame,
            )

            if embedding is None:
                continue

            # Reject samples that are very different from the
            # already collected face samples.
            if embeddings:
                similarity = self.face_engine.cosine_similarity(
                    embedding,
                    embeddings[-1],
                )

                if similarity < self.ENROLLMENT_MIN_SIMILARITY:
                    continue

            embeddings.append(embedding)

            if len(embeddings) >= self.ENROLLMENT_SAMPLES:
                break

        if not embeddings:
            raise ValueError(
                "No valid face samples were captured."
            )

        if len(embeddings) < 3:
            raise ValueError(
                "Not enough valid face samples. "
                "Please capture your face again."
            )

        profile = self.face_engine.build_face_profile(
            embeddings,
        )

        return self._create_user(
            user=user,
            embedding=profile,
        )

    def _create_user(
        self,
        user: UserCreate,
        embedding: np.ndarray,
    ) -> UserResponse:
        """Create the database user using a face profile."""
        embedding_blob = self._embedding_to_blob(
            embedding,
        )

        try:
            with get_connection() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO users (
                        user_code,
                        first_name,
                        last_name,
                        email,
                        phone,
                        face_embedding,
                        embedding_dimension
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user.user_code,
                        user.first_name,
                        user.last_name,
                        user.email,
                        user.phone,
                        embedding_blob,
                        int(embedding.size),
                    ),
                )

                user_id = int(cursor.lastrowid)

                connection.commit()

                row = connection.execute(
                    """
                    SELECT
                        id,
                        user_code,
                        first_name,
                        last_name,
                        email,
                        phone,
                        face_embedding,
                        embedding_dimension,
                        created_at,
                        last_authenticated_at,
                        is_active
                    FROM users
                    WHERE id = ?
                    """,
                    (user_id,),
                ).fetchone()

        except sqlite3.IntegrityError as exc:
            if "user_code" in str(exc).lower():
                raise ValueError(
                    "User code already exists."
                ) from exc

            raise ValueError(
                "Unable to register the user."
            ) from exc

        if row is None:
            raise RuntimeError(
                "User was created but could not be loaded."
            )

        # Force authentication cache to reload.
        self._cache_loaded = False

        return self._row_to_user_response(row)

    # =====================================================
    # Authentication
    # =====================================================

    def authenticate(
        self,
        frame: np.ndarray,
        threshold: float | None = None,
        detection: FaceDetection | None = None,
    ) -> AuthenticationResult:
        """
        Authenticate the largest detected face.

        The camera frame is converted into an SFace embedding
        and compared against all active registered users.
        """
        effective_threshold = (
            settings.face_match_threshold
            if threshold is None
            else threshold
        )

        embedding = self.face_engine.embedding_from_frame(
            frame,
            detection=detection,
        )

        if embedding is None:
            return AuthenticationResult(
                authenticated=False,
                similarity_score=0.0,
                user=None,
                message="No face detected.",
            )

        self._ensure_embedding_cache()

        if not self._embedding_cache:
            return AuthenticationResult(
                authenticated=False,
                similarity_score=0.0,
                user=None,
                message="No registered users found.",
            )

        user_ids = [
            item[0]
            for item in self._embedding_cache
        ]

        embeddings = [
            item[1]
            for item in self._embedding_cache
        ]

        match = self.face_engine.find_best_match(
            query_embedding=embedding,
            stored_embeddings=embeddings,
            threshold=effective_threshold,
        )

        if match is None:
            return AuthenticationResult(
                authenticated=False,
                similarity_score=0.0,
                user=None,
                message="Face not recognized.",
            )

        matched_user_id = user_ids[match.index]

        user = self.get_user(
            matched_user_id,
        )

        if user is None:
            self._cache_loaded = False

            return AuthenticationResult(
                authenticated=False,
                similarity_score=match.similarity,
                user=None,
                message="Matched user could not be loaded.",
            )

        self._record_authentication(
            user.id,
        )

        updated_user = self.get_user(
            user.id,
        )

        return AuthenticationResult(
            authenticated=True,
            similarity_score=match.similarity,
            user=(
                self._user_response_to_list_item(
                    updated_user,
                )
                if updated_user is not None
                else self._user_response_to_list_item(
                    user,
                )
            ),
            message=f"Welcome, {user.first_name}.",
        )

    # =====================================================
    # User retrieval
    # =====================================================

    def get_user(
        self,
        user_id: int,
    ) -> UserResponse | None:
        """Return a user by ID."""
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    user_code,
                    first_name,
                    last_name,
                    email,
                    phone,
                    face_embedding,
                    embedding_dimension,
                    created_at,
                    last_authenticated_at,
                    is_active
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_user_response(
            row,
        )

    def list_users(
        self,
        search: str = "",
    ) -> list[UserListItem]:
        """Return active users, optionally filtered by search text."""
        search = search.strip()

        with get_connection() as connection:
            if search:
                pattern = f"%{search}%"

                rows = connection.execute(
                    """
                    SELECT
                        id,
                        user_code,
                        first_name,
                        last_name,
                        email,
                        phone,
                        created_at,
                        last_authenticated_at,
                        is_active
                    FROM users
                    WHERE is_active = 1
                      AND (
                          user_code LIKE ?
                          OR first_name LIKE ?
                          OR last_name LIKE ?
                          OR email LIKE ?
                          OR phone LIKE ?
                      )
                    ORDER BY first_name COLLATE NOCASE,
                             last_name COLLATE NOCASE
                    """,
                    (
                        pattern,
                        pattern,
                        pattern,
                        pattern,
                        pattern,
                    ),
                ).fetchall()

            else:
                rows = connection.execute(
                    """
                    SELECT
                        id,
                        user_code,
                        first_name,
                        last_name,
                        email,
                        phone,
                        created_at,
                        last_authenticated_at,
                        is_active
                    FROM users
                    WHERE is_active = 1
                    ORDER BY first_name COLLATE NOCASE,
                             last_name COLLATE NOCASE
                    """
                ).fetchall()

        return [
            self._row_to_user_list_item(row)
            for row in rows
        ]


    # =====================================================
    # User management
    # =====================================================

    def update_user(
        self,
        user_id: int,
        user_code: str,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
    ) -> UserResponse:
        """Update editable user information."""

        try:
            with get_connection() as connection:
                connection.execute(
                    """
                    UPDATE users
                    SET
                        user_code = ?,
                        first_name = ?,
                        last_name = ?,
                        email = ?,
                        phone = ?
                    WHERE id = ?
                    """,
                    (
                        user_code,
                        first_name,
                        last_name,
                        email,
                        phone,
                        user_id,
                    ),
                )

                connection.commit()

        except sqlite3.IntegrityError as exc:
            if "user_code" in str(exc).lower():
                raise ValueError(
                    "User code already exists."
                ) from exc

            raise ValueError(
                "Unable to update the user."
            ) from exc

        user = self.get_user(user_id)

        if user is None:
            raise RuntimeError(
                "User was updated but could not be loaded."
            )

        self._cache_loaded = False

        return user

    def deactivate_user(
        self,
        user_id: int,
    ) -> None:
        """Deactivate a user without destroying biometric data."""

        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE users
                SET is_active = 0
                WHERE id = ?
                """,
                (user_id,),
            )

            if cursor.rowcount == 0:
                raise ValueError(
                    "User not found."
                )

            connection.commit()

        self._cache_loaded = False


    # =====================================================
    # Embedding cache
    # =====================================================

    def refresh_embedding_cache(self) -> None:
        """Reload active user face profiles into memory."""
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    face_embedding,
                    embedding_dimension
                FROM users
                WHERE is_active = 1
                """
            ).fetchall()

        cache: list[tuple[int, np.ndarray]] = []

        for row in rows:
            embedding = self._blob_to_embedding(
                row["face_embedding"],
                row["embedding_dimension"],
            )

            if embedding is not None:
                cache.append(
                    (
                        int(row["id"]),
                        embedding,
                    )
                )

        self._embedding_cache = cache
        self._cache_loaded = True

    def _ensure_embedding_cache(self) -> None:
        """Load the embedding cache if necessary."""
        if not self._cache_loaded:
            self.refresh_embedding_cache()

    # =====================================================
    # Authentication timestamp
    # =====================================================

    def _record_authentication(
        self,
        user_id: int,
    ) -> None:
        """Record the latest successful authentication time."""
        authenticated_at = datetime.now(
            timezone.utc,
        ).isoformat()

        with get_connection() as connection:
            connection.execute(
                """
                UPDATE users
                SET last_authenticated_at = ?
                WHERE id = ?
                """,
                (
                    authenticated_at,
                    user_id,
                ),
            )

            connection.commit()

    # =====================================================
    # Serialization
    # =====================================================

    @staticmethod
    def _embedding_to_blob(
        embedding: np.ndarray,
    ) -> bytes:
        """Convert an embedding into SQLite BLOB data."""
        normalized = np.asarray(
            embedding,
            dtype=np.float32,
        ).reshape(-1)

        return normalized.tobytes()

    @staticmethod
    def _blob_to_embedding(
        blob: bytes,
        dimension: int,
    ) -> np.ndarray | None:
        """Convert SQLite BLOB data into a NumPy embedding."""
        if not blob or dimension <= 0:
            return None

        embedding = np.frombuffer(
            blob,
            dtype=np.float32,
        ).copy()

        if embedding.size != dimension:
            return None

        return embedding

    # =====================================================
    # Row conversion
    # =====================================================

    def _row_to_user_response(
        self,
        row: sqlite3.Row,
    ) -> UserResponse:
        """Convert a SQLite row into UserResponse."""
        return UserResponse(
            id=int(row["id"]),
            user_code=row["user_code"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            phone=row["phone"],
            face_embedding=bytes(
                row["face_embedding"],
            ),
            embedding_dimension=int(
                row["embedding_dimension"],
            ),
            created_at=self._parse_datetime(
                row["created_at"],
            ),
            last_authenticated_at=(
                self._parse_optional_datetime(
                    row["last_authenticated_at"],
                )
            ),
            is_active=bool(
                row["is_active"],
            ),
        )

    def _row_to_user_list_item(
        self,
        row: sqlite3.Row,
    ) -> UserListItem:
        """Convert a SQLite row into UserListItem."""
        return UserListItem(
            id=int(row["id"]),
            user_code=row["user_code"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            phone=row["phone"],
            created_at=self._parse_datetime(
                row["created_at"],
            ),
            last_authenticated_at=(
                self._parse_optional_datetime(
                    row["last_authenticated_at"],
                )
            ),
            is_active=bool(
                row["is_active"],
            ),
        )

    @staticmethod
    def _user_response_to_list_item(
        user: UserResponse,
    ) -> UserListItem:
        """Convert a complete user model into a lightweight list model."""
        return UserListItem(
            id=user.id,
            user_code=user.user_code,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            created_at=user.created_at,
            last_authenticated_at=user.last_authenticated_at,
            is_active=user.is_active,
        )

    # =====================================================
    # Datetime helpers
    # =====================================================

    @staticmethod
    def _parse_datetime(
        value: str,
    ) -> datetime:
        """Parse a SQLite datetime value."""
        parsed = datetime.fromisoformat(
            value,
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc,
            )

        return parsed

    @staticmethod
    def _parse_optional_datetime(
        value: str | None,
    ) -> datetime | None:
        """Parse an optional SQLite datetime value."""
        if value is None:
            return None

        return FaceAuthService._parse_datetime(
            value,
        )