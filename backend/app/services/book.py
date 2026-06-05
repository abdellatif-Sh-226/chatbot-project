from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


class BookService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: BookCreate) -> Book:
        book = Book(**data.model_dump())
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def get_all(self) -> List[Book]:
        return self.db.query(Book).order_by(Book.id_livre).all()

    def get_by_id(self, book_id: int) -> Optional[Book]:
        return self.db.query(Book).filter(Book.id_livre == book_id).first()

    def search(self, query: str) -> List[Book]:
        filters = [Book.titre.ilike(f"%{query}%"), Book.auteur.ilike(f"%{query}%")]
        if query.isdigit():
            filters.append(Book.id_livre == int(query))
        return self.db.query(Book).filter(or_(*filters)).order_by(Book.id_livre).all()

    def search_advanced(self, query: Optional[str] = None, categorie: Optional[str] = None, statut: Optional[str] = None, page: int = 1, per_page: int = 10) -> Tuple[List[Book], int]:
        q = self.db.query(Book)
        if query:
            filters = [Book.titre.ilike(f"%{query}%"), Book.auteur.ilike(f"%{query}%")]
            if query.isdigit():
                filters.append(Book.id_livre == int(query))
            q = q.filter(or_(*filters))
        if categorie:
            q = q.filter(Book.categorie.ilike(f"%{categorie}%"))
        if statut:
            q = q.filter(Book.statut == statut)
        total = q.count()
        books = q.order_by(Book.id_livre).offset((page - 1) * per_page).limit(per_page).all()
        return books, total

    def update(self, book_id: int, data: BookUpdate) -> Optional[Book]:
        book = self.get_by_id(book_id)
        if not book:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(book, field, value)
        self.db.commit()
        self.db.refresh(book)
        return book

    def delete(self, book_id: int) -> bool:
        book = self.get_by_id(book_id)
        if not book:
            return False
        self.db.delete(book)
        self.db.commit()
        return True
