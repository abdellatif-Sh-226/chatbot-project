"""
Pydantic schemas for Book CRUD operations.

Defines request validation models and response serialisation
for every book-related endpoint.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BookBase(BaseModel):
    """Shared fields used in create, update, and response schemas."""

    titre: str = Field(..., min_length=1, max_length=255, description="Book title")
    auteur: str = Field(..., min_length=1, max_length=255, description="Author name")
    categorie: str = Field(..., max_length=100, description="Category (Roman, Science, ...)")
    annee_publication: Optional[int] = Field(None, ge=1000, le=2100, description="Publication year")
    quantite_disponible: int = Field(0, ge=0, description="Number of available copies")
    statut: str = Field("disponible", pattern=r"^(disponible|emprunté|réservé)$", description="Book status")


class BookCreate(BookBase):
    """Schema for creating a new book. All base fields are required."""

    pass


class BookUpdate(BaseModel):
    """Schema for updating a book. All fields are optional (partial update)."""

    titre: Optional[str] = Field(None, min_length=1, max_length=255)
    auteur: Optional[str] = Field(None, min_length=1, max_length=255)
    categorie: Optional[str] = Field(None, max_length=100)
    annee_publication: Optional[int] = Field(None, ge=1000, le=2100)
    quantite_disponible: Optional[int] = Field(None, ge=0)
    statut: Optional[str] = Field(None, pattern=r"^(disponible|emprunté|réservé)$")


class BookResponse(BookBase):
    """Schema returned by the API when a book is created, updated, or fetched."""

    id_livre: int

    model_config = {"from_attributes": True}


class BookSearch(BaseModel):
    """Query parameters for searching books."""

    query: str = Field(..., min_length=1, description="Search keyword for title, author, or ID")
