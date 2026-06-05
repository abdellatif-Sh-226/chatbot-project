from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.book import BookResponse, BookCreate, BookUpdate, BookSearchAdvanced, PaginatedBooks
from app.services.book import BookService
from app.core.dependencies import get_current_user, require_admin
from app.models.book import User

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=List[BookResponse])
def list_books(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return BookService(db).get_all()


@router.get("/search", response_model=List[BookResponse])
def search_books(query: str = Query(..., min_length=1), db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return BookService(db).search(query)


@router.get("/advanced", response_model=PaginatedBooks)
def advanced_search(
    query: str | None = Query(None),
    categorie: str | None = Query(None),
    statut: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = BookService(db)
    books, total = service.search_advanced(query, categorie, statut, page, per_page)
    return PaginatedBooks(books=books, total=total, page=page, per_page=per_page, total_pages=max(1, (total + per_page - 1) // per_page))


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    book = BookService(db).get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookResponse, status_code=201)
def create_book(data: BookCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return BookService(db).create(data)


@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, data: BookUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    book = BookService(db).update(book_id, data)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if not BookService(db).delete(book_id):
        raise HTTPException(status_code=404, detail="Book not found")
