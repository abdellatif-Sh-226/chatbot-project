"""
Authentication service layer.

Contains business logic for user registration, login,
and profile retrieval, decoupled from the HTTP layer.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.book import User
from app.schemas.auth import UserCreate, LoginRequest
from app.core.security import hash_password, verify_password, create_access_token


class AuthService:
    """Handles authentication business logic."""

    def __init__(self, db: Session):
        self.db = db

    def register(self, data: UserCreate) -> User:
        """Create a new user account. Raises 409 if username or email already exists."""
        if self.db.query(User).filter(User.username == data.username).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )
        if self.db.query(User).filter(User.email == data.email).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, data: LoginRequest) -> str:
        """Authenticate user and return a JWT access token."""
        user = self.db.query(User).filter(User.username == data.username).first()
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        return create_access_token(data={"sub": user.username})
