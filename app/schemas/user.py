

from datetime import datetime
from typing import Optional
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


# ── Request schemas (what the client sends) 

class UserCreateRequest(BaseModel):
    """Data needed to register a new user."""
    full_name: str       = Field(..., min_length=2, max_length=100, example="Jane Doe")
    email:     EmailStr  = Field(..., example="jane@example.com")
    password:  str       = Field(..., min_length=6, example="secret123")
    role:      UserRole  = Field(default=UserRole.VIEWER, example="viewer")


class UserUpdateRequest(BaseModel):
    """All fields are optional — only send what you want to change."""
    full_name: Optional[str]      = Field(None, min_length=2, max_length=100)
    role:      Optional[UserRole] = None
    is_active: Optional[bool]     = None


class PasswordChangeRequest(BaseModel):
    """Used by a user to change their own password."""
    current_password: str = Field(..., min_length=6)
    new_password:     str = Field(..., min_length=6)


# ── Response schemas (what the API returns) ──────────────────────────────────

class UserResponse(BaseModel):
    """Safe user representation — password is never included."""
    user_id:    int
    full_name:  str
    email:      str
    role:       UserRole
    is_active:  bool
   
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True   # Allows Pydantic to read from ORM objects


# ── Auth schemas ─────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    """Returned after successful login."""
    access_token: str
    token_type:   str = "bearer"
    user:         UserResponse
