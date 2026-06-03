"""
Book service layer.

Contains business logic for all CRUD operations on books,
decoupled from HTTP concerns.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


class BookService:
    """Encapsulates book database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: BookCreate) -> Book:
        """Add a new book to the catalogue."""
        book = Book(**data.model_dump())
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def get_all(self) -> List[Book]:
        """Return every book ordered by id."""
        return self.db.query(Book).order_by(Book.id_livre).all()

    def get_by_id(self, book_id: int) -> Optional[Book]:
        """Fetch a single book by its primary key."""
        return self.db.query(Book).filter(Book.id_livre == book_id).first()

    def search(self, query: str) -> List[Book]:
        """
        Search books by titre, auteur, or id_livre.

        Performs a case-insensitive LIKE match on title and
        author, and an exact match on id if the query is numeric.
        """
        filters = [
            Book.titre.ilike(f"%{query}%"),
            Book.auteur.ilike(f"%{query}%"),
        ]
        if query.isdigit():
            filters.append(Book.id_livre == int(query))

        return self.db.query(Book).filter(or_(*filters)).order_by(Book.id_livre).all()

    def update(self, book_id: int, data: BookUpdate) -> Optional[Book]:
        """Partially update a book. Returns None if not found."""
        book = self.get_by_id(book_id)
        if not book:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(book, field, value)

        self.db.commit()
        self.db.refresh(book)
        return book

    def delete(self, book_id: int) -> bool:
        """Remove a book by id. Returns True if deleted, False if not found."""
        book = self.get_by_id(book_id)
        if not book:
            return False
        self.db.delete(book)
        self.db.commit()
        return True
