from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.stats import StatsService
from app.core.dependencies import get_current_user
from app.models.book import User

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/")
def get_stats(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return StatsService(db).get_stats()
