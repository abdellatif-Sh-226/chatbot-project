"""
Authentication API routes.

Endpoints for user registration, login, and
fetching the current user profile.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import UserCreate, UserResponse, LoginRequest, Token
from app.services.auth import AuthService
from app.core.dependencies import get_current_user
from app.models.book import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    service = AuthService(db)
    return service.register(data)


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and receive a JWT access token."""
    service = AuthService(db)
    access_token = service.login(data)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user
