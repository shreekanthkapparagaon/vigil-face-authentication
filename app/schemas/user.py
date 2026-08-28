from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    """Validated data required to register a new user."""

    user_code: str = Field(min_length=1, max_length=50)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(default="", max_length=100)
    email: str = Field(default="", max_length=255)
    phone: str = Field(default="", max_length=30)


class UserResponse(BaseModel):
    """Complete user data returned by the application."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_code: str
    first_name: str
    last_name: str
    email: str
    phone: str
    face_embedding: bytes
    embedding_dimension: int
    created_at: datetime
    last_authenticated_at: datetime | None
    is_active: bool


class UserListItem(BaseModel):
    """Lightweight user data used by the Users interface."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_code: str
    first_name: str
    last_name: str
    email: str
    phone: str
    created_at: datetime
    last_authenticated_at: datetime | None
    is_active: bool