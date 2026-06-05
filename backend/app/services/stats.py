from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.book import Book, User, Reservation


class StatsService:
    def __init__(self, db: Session):
        self.db = db

    def get_stats(self) -> dict:
        total_books = self.db.query(Book).count()
        total_users = self.db.query(User).count()
        total_reservations = self.db.query(Reservation).count()
        pending_reservations = self.db.query(Reservation).filter(Reservation.status == "pending").count()

        category_counts = self.db.query(Book.categorie, func.count(Book.id_livre)).group_by(Book.categorie).all()
        categories = {cat: count for cat, count in category_counts}

        return {
            "total_books": total_books,
            "total_users": total_users,
            "total_reservations": total_reservations,
            "pending_reservations": pending_reservations,
            "categories": categories,
        }
