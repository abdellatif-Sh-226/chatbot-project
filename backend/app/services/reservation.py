from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from app.models.book import Reservation, Book, User, BorrowedBook


class ReservationService:
    def __init__(self, db: Session):
        self.db = db

    def reserve_book(self, user_id: int, book_id: int) -> Reservation:
        book = self.db.query(Book).filter(Book.id_livre == book_id).first()
        if not book:
            raise ValueError("Book not found")
        if book.quantite_disponible <= 0:
            raise ValueError("No copies available for this book")
        existing = self.db.query(Reservation).filter(
            Reservation.book_id == book_id, Reservation.user_id == user_id,
            Reservation.status.in_(["pending", "accepted", "borrowed"])
        ).first()
        if existing:
            raise ValueError("You already have an active reservation or borrow for this book")
        reservation = Reservation(user_id=user_id, book_id=book_id, status="pending")
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def accept_reservation(self, reservation_id: int) -> Reservation:
        reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            raise ValueError("Reservation not found")
        if reservation.status != "pending":
            raise ValueError("Reservation already processed")
        book = self.db.query(Book).filter(Book.id_livre == reservation.book_id).first()
        if book:
            accepted_count = self.db.query(Reservation).filter(
                Reservation.book_id == book.id_livre,
                Reservation.status.in_(["accepted", "borrowed"])
            ).count()
            if accepted_count >= book.quantite_disponible:
                raise ValueError(f"No more copies available for '{book.titre}' (only {book.quantite_disponible} copy/copies)")
        reservation.status = "accepted"
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def reject_reservation(self, reservation_id: int) -> Reservation:
        reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            raise ValueError("Reservation not found")
        if reservation.status != "pending":
            raise ValueError("Reservation already processed")
        reservation.status = "rejected"
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def confirm_pickup(self, reservation_id: int) -> BorrowedBook:
        reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            raise ValueError("Reservation not found")
        if reservation.status != "accepted":
            raise ValueError("Reservation must be accepted first")
        reservation.status = "borrowed"
        book = self.db.query(Book).filter(Book.id_livre == reservation.book_id).first()
        if book and book.quantite_disponible > 0:
            book.quantite_disponible -= 1
            if book.quantite_disponible == 0:
                book.statut = "indisponible"
        borrowed = BorrowedBook(
            user_id=reservation.user_id,
            book_id=reservation.book_id,
            borrowed_at=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=14),
        )
        self.db.add(borrowed)
        self.db.commit()
        self.db.refresh(borrowed)
        return borrowed

    def cancel_reservation(self, reservation_id: int, user_id: int) -> Reservation:
        reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            raise ValueError("Reservation not found")
        if reservation.user_id != user_id:
            raise ValueError("Not your reservation")
        if reservation.status not in ("pending", "accepted"):
            raise ValueError("Cannot cancel this reservation")
        reservation.status = "cancelled"
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def auto_reject_expired(self):
        now = datetime.utcnow()
        expired = self.db.query(Reservation).filter(
            Reservation.status == "accepted",
            Reservation.updated_at < now - timedelta(hours=48)
        ).all()
        for r in expired:
            r.status = "auto_rejected"
        self.db.commit()
        return len(expired)

    def get_user_reservations(self, user_id: int) -> List[dict]:
        self.auto_reject_expired()
        reservations = self.db.query(Reservation).filter(Reservation.user_id == user_id).order_by(Reservation.created_at.desc()).all()
        result = []
        for r in reservations:
            book = self.db.query(Book).filter(Book.id_livre == r.book_id).first()
            result.append({
                "id": r.id, "user_id": r.user_id, "book_id": r.book_id,
                "status": r.status, "created_at": r.created_at,
                "book_title": book.titre if book else "",
                "username": "",
            })
        return result

    def get_all_reservations(self) -> List[dict]:
        self.auto_reject_expired()
        reservations = self.db.query(Reservation).order_by(Reservation.created_at.desc()).all()
        result = []
        for r in reservations:
            book = self.db.query(Book).filter(Book.id_livre == r.book_id).first()
            user = self.db.query(User).filter(User.id == r.user_id).first()
            result.append({
                "id": r.id, "user_id": r.user_id, "book_id": r.book_id,
                "status": r.status, "created_at": r.created_at,
                "book_title": book.titre if book else "",
                "username": user.username if user else "",
            })
        return result

    def get_accepted_reservations(self) -> List[dict]:
        self.auto_reject_expired()
        reservations = self.db.query(Reservation).filter(
            Reservation.status == "accepted"
        ).order_by(Reservation.created_at.desc()).all()
        result = []
        for r in reservations:
            book = self.db.query(Book).filter(Book.id_livre == r.book_id).first()
            user = self.db.query(User).filter(User.id == r.user_id).first()
            result.append({
                "id": r.id, "user_id": r.user_id, "book_id": r.book_id,
                "status": r.status, "created_at": r.created_at,
                "book_title": book.titre if book else "",
                "username": user.username if user else "",
            })
        return result

    def get_user_borrowed_books(self, user_id: int) -> List[dict]:
        borrowed = self.db.query(BorrowedBook).filter(
            BorrowedBook.user_id == user_id,
            BorrowedBook.returned_at.is_(None)
        ).order_by(BorrowedBook.borrowed_at.desc()).all()
        result = []
        now = datetime.utcnow()
        for b in borrowed:
            book = self.db.query(Book).filter(Book.id_livre == b.book_id).first()
            user = self.db.query(User).filter(User.id == b.user_id).first()
            days = (b.due_date - now).days if b.due_date else 0
            result.append({
                "id": b.id,
                "user_id": b.user_id,
                "book_id": b.book_id,
                "book_title": book.titre if book else "",
                "username": user.username if user else "",
                "borrowed_at": b.borrowed_at,
                "due_date": b.due_date,
                "returned_at": b.returned_at,
                "days_remaining": max(0, days),
            })
        return result

    def get_all_borrowed_books(self) -> List[dict]:
        borrowed = self.db.query(BorrowedBook).filter(
            BorrowedBook.returned_at.is_(None)
        ).order_by(BorrowedBook.borrowed_at.desc()).all()
        result = []
        now = datetime.utcnow()
        for b in borrowed:
            book = self.db.query(Book).filter(Book.id_livre == b.book_id).first()
            user = self.db.query(User).filter(User.id == b.user_id).first()
            days = (b.due_date - now).days if b.due_date else 0
            result.append({
                "id": b.id,
                "user_id": b.user_id,
                "book_id": b.book_id,
                "book_title": book.titre if book else "",
                "username": user.username if user else "",
                "borrowed_at": b.borrowed_at,
                "due_date": b.due_date,
                "returned_at": b.returned_at,
                "days_remaining": max(0, days),
            })
        return result

    def return_book_admin(self, borrowed_id: int) -> BorrowedBook:
        borrowed = self.db.query(BorrowedBook).filter(BorrowedBook.id == borrowed_id).first()
        if not borrowed:
            raise ValueError("Borrowed book not found")
        if borrowed.returned_at is not None:
            raise ValueError("Book already returned")
        borrowed.returned_at = datetime.utcnow()
        reservation = self.db.query(Reservation).filter(
            Reservation.user_id == borrowed.user_id,
            Reservation.book_id == borrowed.book_id,
            Reservation.status == "borrowed"
        ).first()
        if reservation:
            reservation.status = "returned"
        book = self.db.query(Book).filter(Book.id_livre == borrowed.book_id).first()
        if book:
            book.quantite_disponible += 1
            if book.statut == "indisponible":
                book.statut = "disponible"
        self.db.commit()
        self.db.refresh(borrowed)
        return borrowed
