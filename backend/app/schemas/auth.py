"""
Pydantic schemas for authentication (JWT).

Defines request/response models for user registration,
login, and token exchange.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    """Schema for registering a new user."""

    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserResponse(BaseModel):
    """Schema returned after registration or profile fetch."""

    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Schema for user login (username + password)."""

    username: str
    password: str


class Token(BaseModel):
    """JWT token returned on successful authentication."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Contents of the decoded JWT token."""

    sub: Optional[str] = None
    exp: Optional[int] = None
