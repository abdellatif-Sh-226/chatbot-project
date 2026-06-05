from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.book import BorrowedBookResponse
from app.services.reservation import ReservationService
from app.core.dependencies import get_current_user, require_admin
from app.models.book import User, Book

router = APIRouter(prefix="/borrowed", tags=["Borrowed Books"])


@router.get("/me", response_model=List[BorrowedBookResponse])
def my_borrowed_books(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ReservationService(db).get_user_borrowed_books(current_user.id)


@router.get("/all", response_model=List[BorrowedBookResponse])
def all_borrowed_books(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return ReservationService(db).get_all_borrowed_books()


@router.post("/{borrowed_id}/return", response_model=BorrowedBookResponse)
def return_borrowed_book(borrowed_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    try:
        borrowed = ReservationService(db).return_book_admin(borrowed_id)
        book = db.query(Book).filter(Book.id_livre == borrowed.book_id).first()
        user = db.query(User).filter(User.id == borrowed.user_id).first()
        return {
            "id": borrowed.id,
            "user_id": borrowed.user_id,
            "book_id": borrowed.book_id,
            "book_title": book.titre if book else "",
            "username": user.username if user else "",
            "borrowed_at": borrowed.borrowed_at,
            "due_date": borrowed.due_date,
            "returned_at": borrowed.returned_at,
            "days_remaining": 0,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
