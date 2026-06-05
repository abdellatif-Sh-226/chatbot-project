from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id_livre = Column(Integer, primary_key=True, autoincrement=True)
    titre = Column(String(255), nullable=False, index=True)
    auteur = Column(String(255), nullable=False, index=True)
    categorie = Column(String(100), nullable=False)
    annee_publication = Column(Integer, nullable=True)
    quantite_disponible = Column(Integer, default=0, nullable=False)
    statut = Column(String(50), default="disponible", nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    reservations = relationship("Reservation", back_populates="book")
    borrowed_books = relationship("BorrowedBook", back_populates="book")

    def __repr__(self):
        return f"<Book(id={self.id_livre}, titre='{self.titre}')>"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default="member", nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    reservations = relationship("Reservation", back_populates="user")
    borrowed_books = relationship("BorrowedBook", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id_livre"), nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="reservations")
    book = relationship("Book", back_populates="reservations")

    def __repr__(self):
        return f"<Reservation(id={self.id}, user={self.user_id}, book={self.book_id})>"


class BorrowedBook(Base):
    __tablename__ = "borrowed_books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id_livre"), nullable=False)
    borrowed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    due_date = Column(DateTime, nullable=False)
    returned_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="borrowed_books")
    book = relationship("Book", back_populates="borrowed_books")

    def __repr__(self):
        return f"<BorrowedBook(id={self.id}, user={self.user_id}, book={self.book_id})>"
