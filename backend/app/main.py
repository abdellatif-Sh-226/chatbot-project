from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api.auth import router as auth_router
from app.api.books import router as books_router
from app.api.chat import router as chat_router

from app.api.reservation import router as reservation_router
from app.api.stats import router as stats_router
from app.api.admin_users import router as admin_users_router
from app.api.borrowed import router as borrowed_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth_router)
app.include_router(books_router)
app.include_router(chat_router)
app.include_router(reservation_router)
app.include_router(stats_router)
app.include_router(admin_users_router)
app.include_router(borrowed_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
