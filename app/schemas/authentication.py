from pydantic import BaseModel, Field

from app.schemas.user import UserListItem


class AuthenticationRequest(BaseModel):
    """Input data for a face authentication attempt."""

    threshold: float = Field(
        default=0.60,
        ge=0.0,
        le=1.0,
    )


class AuthenticationResult(BaseModel):
    """Result returned after attempting face authentication."""

    authenticated: bool
    similarity_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )
    user: UserListItem | None = None
    message: str