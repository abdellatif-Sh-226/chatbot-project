from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.book import ReservationCreate, ReservationResponse, BorrowedBookResponse
from app.services.reservation import ReservationService
from app.core.dependencies import get_current_user, require_admin
from app.models.book import User, Book

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.post("/", response_model=ReservationResponse, status_code=201)
def reserve_book(data: ReservationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        reservation = ReservationService(db).reserve_book(current_user.id, data.book_id)
        return ReservationResponse(**{
            "id": reservation.id, "user_id": reservation.user_id, "book_id": reservation.book_id,
            "status": reservation.status, "created_at": reservation.created_at,
            "book_title": reservation.book.titre, "username": current_user.username,
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{reservation_id}/accept", response_model=ReservationResponse)
def accept_reservation(reservation_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    try:
        r = ReservationService(db).accept_reservation(reservation_id)
        return ReservationResponse(**{
            "id": r.id, "user_id": r.user_id, "book_id": r.book_id,
            "status": r.status, "created_at": r.created_at,
            "book_title": r.book.titre, "username": "",
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{reservation_id}/reject", response_model=ReservationResponse)
def reject_reservation(reservation_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    try:
        r = ReservationService(db).reject_reservation(reservation_id)
        return ReservationResponse(**{
            "id": r.id, "user_id": r.user_id, "book_id": r.book_id,
            "status": r.status, "created_at": r.created_at,
            "book_title": r.book.titre, "username": "",
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{reservation_id}/pickup", response_model=BorrowedBookResponse)
def confirm_pickup(reservation_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    try:
        borrowed = ReservationService(db).confirm_pickup(reservation_id)
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
            "days_remaining": 14,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{reservation_id}/cancel", response_model=ReservationResponse)
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        reservation = ReservationService(db).cancel_reservation(reservation_id, current_user.id)
        return ReservationResponse(**{
            "id": reservation.id, "user_id": reservation.user_id, "book_id": reservation.book_id,
            "status": reservation.status, "created_at": reservation.created_at,
            "book_title": reservation.book.titre, "username": "",
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=List[ReservationResponse])
def my_reservations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ReservationService(db).get_user_reservations(current_user.id)


@router.get("/", response_model=List[ReservationResponse])
def all_reservations(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return ReservationService(db).get_all_reservations()


@router.get("/accepted", response_model=List[ReservationResponse])
def accepted_reservations(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return ReservationService(db).get_accepted_reservations()
