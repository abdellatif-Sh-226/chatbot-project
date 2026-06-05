from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field


class BookBase(BaseModel):
    titre: str = Field(..., min_length=1, max_length=255)
    auteur: str = Field(..., min_length=1, max_length=255)
    categorie: str = Field(..., max_length=100)
    annee_publication: Optional[int] = Field(None, ge=1000, le=2100)
    quantite_disponible: int = Field(0, ge=0)
    statut: str = Field("disponible", pattern=r"^(disponible|emprunté|réservé|indisponible)$")


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    titre: Optional[str] = Field(None, min_length=1, max_length=255)
    auteur: Optional[str] = Field(None, min_length=1, max_length=255)
    categorie: Optional[str] = Field(None, max_length=100)
    annee_publication: Optional[int] = Field(None, ge=1000, le=2100)
    quantite_disponible: Optional[int] = Field(None, ge=0)
    statut: Optional[str] = Field(None, pattern=r"^(disponible|emprunté|réservé|indisponible)$")


class BookResponse(BookBase):
    id_livre: int
    model_config = {"from_attributes": True}


class BookSearchAdvanced(BaseModel):
    query: Optional[str] = Field(None, min_length=1)
    categorie: Optional[str] = None
    statut: Optional[str] = Field(None, pattern=r"^(disponible|emprunté|réservé|indisponible)$")
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)


class PaginatedBooks(BaseModel):
    books: List[BookResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class ReservationCreate(BaseModel):
    book_id: int


class BorrowedBookResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    book_title: str = ""
    username: str = ""
    borrowed_at: datetime
    due_date: datetime
    returned_at: Optional[datetime] = None
    days_remaining: Optional[int] = None

    model_config = {"from_attributes": True}


class ReservationResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    status: str
    created_at: datetime
    book_title: str = ""
    username: str = ""

    model_config = {"from_attributes": True}
