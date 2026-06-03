"""
Book and User ORM models for the library management system.

Each model maps to a MySQL table. SQLAlchemy will
automatically create these tables on application startup
(see main.py lifespan).
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base


class Book(Base):
    """
    Represents a book in the library catalogue.

    Fields match the project specification exactly:
    id_livre, titre, auteur, categorie, annee_publication,
    quantite_disponible, statut.
    """

    __tablename__ = "books"

    id_livre = Column(Integer, primary_key=True, autoincrement=True)
    titre = Column(String(255), nullable=False, index=True)
    auteur = Column(String(255), nullable=False, index=True)
    categorie = Column(String(100), nullable=False)
    annee_publication = Column(Integer, nullable=True)
    quantite_disponible = Column(Integer, default=0, nullable=False)
    statut = Column(String(50), default="disponible", nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Book(id={self.id_livre}, titre='{self.titre}')>"


class User(Base):
    """
    Registered user who can authenticate via JWT.

    Only administrators / librarians will use the system,
    so this model is kept minimal.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"
