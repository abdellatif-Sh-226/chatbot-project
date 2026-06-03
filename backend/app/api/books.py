"""
Book CRUD API routes.

All endpoints require JWT authentication (see dependencies).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.book import BookCreate, BookUpdate, BookResponse, BookSearch
from app.services.book import BookService
from app.core.dependencies import get_current_user
from app.models.book import User

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=List[BookResponse])
def list_books(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Retrieve all books in the library."""
    service = BookService(db)
    return service.get_all()


@router.get("/search", response_model=List[BookResponse])
def search_books(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Search books by title, author, or ID."""
    service = BookService(db)
    return service.search(query)


@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Fetch a single book by its ID."""
    service = BookService(db)
    book = service.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookResponse, status_code=201)
def create_book(
    data: BookCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Add a new book to the catalogue."""
    service = BookService(db)
    return service.create(data)


@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    data: BookUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Update an existing book (partial update supported)."""
    service = BookService(db)
    book = service.update(book_id, data)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Remove a book from the catalogue."""
    service = BookService(db)
    if not service.delete(book_id):
        raise HTTPException(status_code=404, detail="Book not found")
