"""
FastAPI application entry point.

Initialises the app, includes all routers, and
creates database tables on startup if they do not exist.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api.auth import router as auth_router
from app.api.books import router as books_router
from app.api.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Create all database tables on startup.
    SQLAlchemy will generate CREATE TABLE statements
    for every model that inherits from Base.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Allow CORS so the Tkinter frontend can communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth_router)
app.include_router(books_router)
app.include_router(chat_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health-check endpoint to verify the API is running."""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
