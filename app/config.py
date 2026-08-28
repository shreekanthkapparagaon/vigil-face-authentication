from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "face_auth.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")


# ---------------------------------------------------------
# Application settings
# ---------------------------------------------------------


class AppSettings(BaseModel):
    """Application-wide configuration."""

    app_name: str = "Face Authentication"
    app_version: str = "0.1.0"

    camera_index: int = Field(default=0, ge=0)
    camera_width: int = Field(default=640, ge=320)
    camera_height: int = Field(default=480, ge=240)
    camera_fps: int = Field(default=30, ge=1, le=120)

    face_match_threshold: float = Field(
        default=0.60,
        ge=0.0,
        le=1.0,
    )

    face_detection_scale: float = Field(
        default=0.5,
        gt=0.0,
        le=1.0,
    )


settings = AppSettings()