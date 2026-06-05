from typing import Any, Optional
from sqlalchemy.orm import Session
from google.genai.types import FunctionDeclaration, Tool

from app.models.book import Book, User, Reservation, BorrowedBook
from app.schemas.book import BookCreate, BookUpdate
from app.services.book import BookService
from app.services.reservation import ReservationService
from app.services.stats import StatsService


def _format_book(b: Book) -> str:
    return (
        f"[{b.id_livre}] '{b.titre}' by {b.auteur} "
        f"[{b.categorie}, {b.annee_publication or 'N/A'}] "
        f"Status: {b.statut}, Copies: {b.quantite_disponible}"
    )


# ---------------------------------------------------------------------------
# Handlers (return a string for the AI)
# ---------------------------------------------------------------------------

def _search_books(db: Session, user: User, args: dict) -> str:
    query = args.get("query", "")
    books = BookService(db).search(query)
    if not books:
        return f"No books found for '{query}'."
    return "Found books:\n" + "\n".join(_format_book(b) for b in books[:20])


def _get_book(db: Session, user: User, args: dict) -> str:
    book = BookService(db).get_by_id(args["book_id"])
    if not book:
        return f"Book ID {args['book_id']} not found."
    return _format_book(book)


def _add_book(db: Session, user: User, args: dict) -> str:
    if user.role != "admin":
        return "Permission denied. Admin only."
    data = BookCreate(
        titre=args["titre"],
        auteur=args["auteur"],
        categorie=args["categorie"],
        annee_publication=args.get("annee"),
        quantite_disponible=args.get("quantite", 1),
        statut=args.get("statut", "disponible"),
    )
    book = BookService(db).create(data)
    return f"Book added successfully: {_format_book(book)}"


def _update_book(db: Session, user: User, args: dict) -> str:
    if user.role != "admin":
        return "Permission denied. Admin only."
    data = BookUpdate(**{k: v for k, v in args.items() if k != "book_id"})
    book = BookService(db).update(args["book_id"], data)
    if not book:
        return f"Book ID {args['book_id']} not found."
    return f"Book updated: {_format_book(book)}"


def _delete_book(db: Session, user: User, args: dict) -> str:
    if user.role != "admin":
        return "Permission denied. Admin only."
    ok = BookService(db).delete(args["book_id"])
    return f"Book ID {args['book_id']} deleted." if ok else "Book not found."


def _reserve_book(db: Session, user: User, args: dict) -> str:
    try:
        rsv = ReservationService(db).reserve_book(user.id, args["book_id"])
        return f"Reservation created (ID {rsv.id}) for book ID {args['book_id']}. Status: pending."
    except ValueError as e:
        return str(e)


def _cancel_reservation(db: Session, user: User, args: dict) -> str:
    try:
        ReservationService(db).cancel_reservation(args["reservation_id"], user.id)
        return f"Reservation ID {args['reservation_id']} cancelled."
    except ValueError as e:
        return str(e)


def _accept_reservation(db: Session, user: User, args: dict) -> str:
    if user.role != "admin":
        return "Permission denied. Admin only."
    try:
        rsv = ReservationService(db).accept_reservation(args["reservation_id"])
        return f"Reservation ID {rsv.id} accepted."
    except ValueError as e:
        return str(e)


def _reject_reservation(db: Session, user: User, args: dict) -> str:
    if user.role != "admin":
        return "Permission denied. Admin only."
    try:
        rsv = ReservationService(db).reject_reservation(args["reservation_id"])
        return f"Reservation ID {rsv.id} rejected."
    except ValueError as e:
        return str(e)


def _confirm_pickup(db: Session, user: User, args: dict) -> str:
    if user.role != "admin":
        return "Permission denied. Admin only."
    try:
        borrowed = ReservationService(db).confirm_pickup(args["reservation_id"])
        return f"Pickup confirmed! Borrowed record ID {borrowed.id} created, due {borrowed.due_date.date()}."
    except ValueError as e:
        return str(e)


def _return_book(db: Session, user: User, args: dict) -> str:
    if user.role != "admin":
        return "Permission denied. Admin only."
    try:
        ReservationService(db).return_book_admin(args["borrowed_id"])
        return f"Borrowed book ID {args['borrowed_id']} returned successfully."
    except ValueError as e:
        return str(e)


def _list_my_borrowed(db: Session, user: User, args: dict) -> str:
    books = ReservationService(db).get_user_borrowed_books(user.id)
    if not books:
        return "You have no borrowed books."
    lines = []
    for b in books:
        lines.append(
            f"- ID {b['id']}: '{b['book_title']}' "
            f"(borrowed: {b['borrowed_at'].date()}, due: {b['due_date'].date()}, "
            f"{b['days_remaining']} days left)"
        )
    return "Your borrowed books:\n" + "\n".join(lines)


def _list_all_users(db: Session, user: User, args: dict) -> str:
    if user.role != "admin":
        return "Permission denied. Admin only."
    users = db.query(User).order_by(User.id).all()
    if not users:
        return "No users found."
    lines = [f"- ID {u.id}: {u.username} ({u.email}) [role: {u.role}, active: {u.is_active}]" for u in users]
    return "All users:\n" + "\n".join(lines)


def _delete_user(db: Session, user: User, args: dict) -> str:
    if user.role != "admin":
        return "Permission denied. Admin only."
    u = db.query(User).filter(User.id == args["user_id"]).first()
    if not u:
        return f"User ID {args['user_id']} not found."
    if u.id == user.id:
        return "Cannot delete yourself."
    db.delete(u)
    db.commit()
    return f"User '{u.username}' (ID {u.id}) deleted."


def _update_user_role(db: Session, user: User, args: dict) -> str:
    if user.role != "admin":
        return "Permission denied. Admin only."
    u = db.query(User).filter(User.id == args["user_id"]).first()
    if not u:
        return f"User ID {args['user_id']} not found."
    u.role = args["role"]
    db.commit()
    return f"User '{u.username}' role changed to '{args['role']}'."


def _get_stats(db: Session, user: User, args: dict) -> str:
    stats = StatsService(db).get_stats()
    return (
        f"Library Statistics:\n"
        f"- Total books: {stats['total_books']}\n"
        f"- Total users: {stats['total_users']}\n"
        f"- Total reservations: {stats['total_reservations']}\n"
        f"- Pending reservations: {stats['pending_reservations']}\n"
        f"- Categories: {', '.join(f'{k}: {v}' for k, v in stats['categories'].items())}"
    )


def _list_all_reservations(db: Session, user: User, args: dict) -> str:
    if user.role != "admin":
        return "Permission denied. Admin only."
    reservations = ReservationService(db).get_all_reservations()
    if not reservations:
        return "No reservations."
    lines = [
        f"- ID {r['id']}: '{r['book_title']}' by {r['username']} [status: {r['status']}, created: {r['created_at'].date()}]"
        for r in reservations
    ]
    return "All reservations:\n" + "\n".join(lines[:30])


def _list_all_borrowed(db: Session, user: User, args: dict) -> str:
    if user.role != "admin":
        return "Permission denied. Admin only."
    books = ReservationService(db).get_all_borrowed_books()
    if not books:
        return "No borrowed books."
    lines = [
        f"- ID {b['id']}: '{b['book_title']}' by {b['username']} "
        f"(borrowed: {b['borrowed_at'].date()}, due: {b['due_date'].date()}, "
        f"{b['days_remaining']} days left)"
        for b in books
    ]
    return "All borrowed books:\n" + "\n".join(lines[:30])


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

HANDLERS = {
    "search_books": (_search_books, {
        "name": "search_books",
        "description": "Search books by title, author, or keyword. Returns matching books.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Search keyword (title or author)"}
            },
            "required": ["query"],
        },
    }),
    "get_book": (_get_book, {
        "name": "get_book",
        "description": "Get detailed information about a specific book by its ID.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "book_id": {"type": "INTEGER", "description": "ID of the book"}
            },
            "required": ["book_id"],
        },
    }),
    "add_book": (_add_book, {
        "name": "add_book",
        "description": "Add a new book to the library. Admin only.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "titre": {"type": "STRING", "description": "Book title"},
                "auteur": {"type": "STRING", "description": "Author name"},
                "categorie": {"type": "STRING", "description": "Category (e.g. Fiction, Science, etc.)"},
                "annee": {"type": "INTEGER", "description": "Publication year (optional)"},
                "quantite": {"type": "INTEGER", "description": "Number of copies (default 1)"},
                "statut": {"type": "STRING", "description": "Status: disponible, emprunté, réservé, indisponible"},
            },
            "required": ["titre", "auteur", "categorie"],
        },
    }),
    "update_book": (_update_book, {
        "name": "update_book",
        "description": "Update a book's details. Admin only.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "book_id": {"type": "INTEGER", "description": "ID of the book to update"},
                "titre": {"type": "STRING", "description": "New title"},
                "auteur": {"type": "STRING", "description": "New author"},
                "categorie": {"type": "STRING", "description": "New category"},
                "annee_publication": {"type": "INTEGER", "description": "New publication year"},
                "quantite_disponible": {"type": "INTEGER", "description": "New available copies count"},
                "statut": {"type": "STRING", "description": "New status"},
            },
            "required": ["book_id"],
        },
    }),
    "delete_book": (_delete_book, {
        "name": "delete_book",
        "description": "Delete a book from the library. Admin only.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "book_id": {"type": "INTEGER", "description": "ID of the book to delete"}
            },
            "required": ["book_id"],
        },
    }),
    "reserve_book": (_reserve_book, {
        "name": "reserve_book",
        "description": "Reserve a book for yourself. Creates a pending reservation.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "book_id": {"type": "INTEGER", "description": "ID of the book to reserve"}
            },
            "required": ["book_id"],
        },
    }),
    "cancel_my_reservation": (_cancel_reservation, {
        "name": "cancel_my_reservation",
        "description": "Cancel one of your own pending or accepted reservations.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "reservation_id": {"type": "INTEGER", "description": "ID of the reservation to cancel"}
            },
            "required": ["reservation_id"],
        },
    }),
    "accept_reservation": (_accept_reservation, {
        "name": "accept_reservation",
        "description": "Accept a pending reservation. Admin only.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "reservation_id": {"type": "INTEGER", "description": "ID of the reservation to accept"}
            },
            "required": ["reservation_id"],
        },
    }),
    "reject_reservation": (_reject_reservation, {
        "name": "reject_reservation",
        "description": "Reject a pending reservation. Admin only.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "reservation_id": {"type": "INTEGER", "description": "ID of the reservation to reject"}
            },
            "required": ["reservation_id"],
        },
    }),
    "confirm_pickup": (_confirm_pickup, {
        "name": "confirm_pickup",
        "description": "Confirm that a user has picked up their accepted reservation (converts to borrowed). Admin only.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "reservation_id": {"type": "INTEGER", "description": "ID of the accepted reservation"}
            },
            "required": ["reservation_id"],
        },
    }),
    "return_book": (_return_book, {
        "name": "return_book",
        "description": "Mark a borrowed book as returned. Admin only.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "borrowed_id": {"type": "INTEGER", "description": "ID of the borrowed book record"}
            },
            "required": ["borrowed_id"],
        },
    }),
    "list_my_borrowed_books": (_list_my_borrowed, {
        "name": "list_my_borrowed_books",
        "description": "List all books you currently have borrowed.",
        "parameters": {
            "type": "OBJECT",
            "properties": {},
            "required": [],
        },
    }),
    "list_all_users": (_list_all_users, {
        "name": "list_all_users",
        "description": "List all registered users with their details. Admin only.",
        "parameters": {
            "type": "OBJECT",
            "properties": {},
            "required": [],
        },
    }),
    "delete_user": (_delete_user, {
        "name": "delete_user",
        "description": "Delete a user from the system. Admin only. Cannot delete yourself.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "user_id": {"type": "INTEGER", "description": "ID of the user to delete"}
            },
            "required": ["user_id"],
        },
    }),
    "update_user_role": (_update_user_role, {
        "name": "update_user_role",
        "description": "Change a user's role (admin or member). Admin only.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "user_id": {"type": "INTEGER", "description": "ID of the user"},
                "role": {"type": "STRING", "description": "New role: 'admin' or 'member'"},
            },
            "required": ["user_id", "role"],
        },
    }),
    "get_library_stats": (_get_stats, {
        "name": "get_library_stats",
        "description": "Get library statistics: total books, users, reservations, pending, and categories.",
        "parameters": {
            "type": "OBJECT",
            "properties": {},
            "required": [],
        },
    }),
    "list_all_reservations": (_list_all_reservations, {
        "name": "list_all_reservations",
        "description": "List ALL reservations (every user). Admin only.",
        "parameters": {
            "type": "OBJECT",
            "properties": {},
            "required": [],
        },
    }),
    "list_all_borrowed_books": (_list_all_borrowed, {
        "name": "list_all_borrowed_books",
        "description": "List ALL currently borrowed books (every user). Admin only.",
        "parameters": {
            "type": "OBJECT",
            "properties": {},
            "required": [],
        },
    }),
}


def get_available_tools() -> list[Tool]:
    declarations = [
        FunctionDeclaration(**spec)
        for _handler, spec in HANDLERS.values()
    ]
    return [Tool(function_declarations=declarations)]


def execute_tool(db: Session, user: User, name: str, args: dict) -> str:
    entry = HANDLERS.get(name)
    if not entry:
        return f"Unknown tool: {name}"
    handler, _spec = entry
    return handler(db, user, args)
