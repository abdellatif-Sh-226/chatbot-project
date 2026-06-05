"""
Chatbot service layer.

Queries the database for book data, builds a context-rich
prompt, and sends it to the Google Gemini API. Falls back
to a local keyword-matching strategy when the API is
unavailable or not configured.
"""

import re
from typing import List, Optional
from sqlalchemy.orm import Session
from google.genai import types
from app.models.book import Book, User
from app.config import settings
from app.tools import get_available_tools, execute_tool


class ChatService:
    """AI-powered library chatbot."""

    def __init__(self, db: Session):
        self.db = db
        self._model = None
        self._client = None

    # ------------------------------------------------------------------
    # AI API integration (Google Gemini)
    # ------------------------------------------------------------------

    def _get_gemini_model(self):
        if self._model is not None:
            return self._model

        if not settings.AI_API_KEY:
            self._model = False
            return None

        try:
            from google import genai
            self._client = genai.Client(api_key=settings.AI_API_KEY)
            self._model = settings.AI_MODEL
            return self._model
        except Exception as e:
            print(f"[ChatService] Failed to init Gemini client: {e}")
            self._model = False
            return None

    def _build_library_context(self, user: Optional["User"] = None) -> str:
        parts = []

        books: List[Book] = self.db.query(Book).order_by(Book.id_livre).all()
        if books:
            lines = []
            for b in books:
                lines.append(
                    f"- ID {b.id_livre}: '{b.titre}' by {b.auteur} "
                    f"[{b.categorie}, {b.annee_publication or 'N/A'}] "
                    f"Status: {b.statut}, Copies available: {b.quantite_disponible}"
                )
            parts.append("=== ALL BOOKS ===\n" + "\n".join(lines))
        else:
            parts.append("=== ALL BOOKS ===\nThe library is currently empty.")

        if not user:
            return "\n\n".join(parts)

        if user.role == "admin":
            from app.models.book import Reservation, BorrowedBook

            all_reservations = self.db.query(Reservation).order_by(Reservation.id).all()
            if all_reservations:
                lines = []
                for r in all_reservations:
                    lines.append(
                        f"- ID {r.id}: '{r.book.titre}' by {r.book.auteur} "
                        f"(user: {r.user.username}, status: {r.status}, created: {r.created_at.date()})"
                    )
                parts.append("=== ALL RESERVATIONS ===\n" + "\n".join(lines))
            else:
                parts.append("=== ALL RESERVATIONS ===\nNo reservations.")

            borrow_requests = self.db.query(Reservation).filter(Reservation.status == "accepted").order_by(Reservation.id).all()
            if borrow_requests:
                lines = []
                for r in borrow_requests:
                    lines.append(
                        f"- ID {r.id}: '{r.book.titre}' by {r.book.auteur} "
                        f"(user: {r.user.username}, accepted: {r.updated_at.date()})"
                    )
                parts.append("=== BORROW REQUESTS (accepted, awaiting pickup) ===\n" + "\n".join(lines))
            else:
                parts.append("=== BORROW REQUESTS ===\nNo borrow requests.")

            all_borrowed = self.db.query(BorrowedBook).order_by(BorrowedBook.id).all()
            if all_borrowed:
                lines = []
                for bb in all_borrowed:
                    lines.append(
                        f"- ID {bb.id}: '{bb.book.titre}' by {bb.book.auteur} "
                        f"(user: {bb.user.username}, borrowed: {bb.borrowed_at.date()}, "
                        f"due: {bb.due_date.date()}"
                        + (f", returned: {bb.returned_at.date()}" if bb.returned_at else ", not yet returned")
                        + ")"
                    )
                parts.append("=== ALL BORROWED BOOKS ===\n" + "\n".join(lines))
            else:
                parts.append("=== ALL BORROWED BOOKS ===\nNo borrowed books.")
        else:
            borrowings = user.borrowed_books
            if borrowings:
                lines = []
                for bb in borrowings:
                    lines.append(
                        f"- ID {bb.id}: '{bb.book.titre}' by {bb.book.auteur} "
                        f"(borrowed: {bb.borrowed_at.date()}, due: {bb.due_date.date()}"
                        + (f", returned: {bb.returned_at.date()}" if bb.returned_at else ", not yet returned")
                        + ")"
                    )
                parts.append("=== MY BORROWED BOOKS ===\n" + "\n".join(lines))
            else:
                parts.append("=== MY BORROWED BOOKS ===\nNo borrowed books.")

            reservations = user.reservations
            if reservations:
                lines = []
                for r in reservations:
                    lines.append(
                        f"- ID {r.id}: '{r.book.titre}' by {r.book.auteur} "
                        f"[status: {r.status}, created: {r.created_at.date()}]"
                    )
                parts.append("=== MY RESERVATIONS ===\n" + "\n".join(lines))
            else:
                parts.append("=== MY RESERVATIONS ===\nNo reservations.")

        return "\n\n".join(parts)

    def _ask_ai(self, user_message: str, context: str, user: Optional["User"] = None) -> Optional[str]:
        model_name = self._get_gemini_model()
        if not model_name:
            return None

        role_label = "Administrator" if user and user.role == "admin" else "Member"
        user_intro = f"Current user: {user.username} (role: {role_label})" if user else "Current user: Guest"
        system_prompt = (
            "You are a library assistant named SmartLib. "
            "Only introduce yourself if the user greets you. "
            "Otherwise answer briefly and naturally. "
            "Always respond in the same language the user used. "
            "Use the available functions to search, modify, or manage library data when needed. "
            "Do NOT ask the user to call a function themselves — call it for them.\n\n"
            f"{user_intro}\n\n"
            f"Library data:\n{context}"
        )

        tools = get_available_tools()
        config = {
            "systemInstruction": system_prompt,
            "temperature": 0.3,
            "maxOutputTokens": 1024,
            "tools": tools,
        }

        try:
            response = self._client.models.generate_content(
                model=model_name,
                contents=user_message,
                config=config,
            )
            return self._handle_gemini_response(response, user_message, model_name, config, user)
        except Exception as e:
            err = str(e)
            print(f"[ChatService] Gemini generate_content failed: {err[:200]}")
            if "429" in err or "quota" in err.lower() or "RESOURCE_EXHAUSTED" in err:
                return "I'm sorry, the AI service quota has been exceeded for today. Please wait until it resets or use a different API key."
            return f"I'm sorry, the AI service encountered an error: {err[:100]}"

    def _handle_gemini_response(self, response, user_message: str, model_name: str, config: dict, user: Optional["User"] = None) -> str:
        candidate = response.candidates[0]
        part = candidate.content.parts[0]

        if part.function_call:
            fc = part.function_call
            print(f"[ChatService] Function call: {fc.name}({fc.args})")
            try:
                result = execute_tool(self.db, user, fc.name, {k: v for k, v in fc.args.items()})
            except Exception as e:
                result = f"Error executing {fc.name}: {e}"
            print(f"[ChatService] Function result: {result[:100]}...")

            response2 = self._client.models.generate_content(
                model=model_name,
                contents=[
                    user_message,
                    types.Content(role="model", parts=[types.Part(function_call=fc)]),
                    types.Content(role="function", parts=[types.Part(
                        function_response=types.FunctionResponse(name=fc.name, response={"result": result})
                    )]),
                ],
                config=config,
            )
            return response2.text.strip() if response2.text else "Done."

        return response.text.strip()

    # ------------------------------------------------------------------
    # Local fallback (keyword matching)
    # ------------------------------------------------------------------

    def _fallback_reply(self, user_message: str) -> str:
        """
        Simple keyword-based fallback when the AI API is unavailable.
        """
        msg = user_message.lower()
        books = self.db.query(Book).order_by(Book.id_livre).all()

        # --- Check for ID lookup ---
        id_match = re.search(r"(?:id|ID|#)\s*(\d+)", user_message)
        if id_match:
            book_id = int(id_match.group(1))
            book = next((b for b in books if b.id_livre == book_id), None)
            if book:
                return (
                    f"Yes, this book exists in the library.\n"
                    f"   Title   : {book.titre}\n"
                    f"   Author  : {book.auteur}\n"
                    f"   Status  : {book.statut} ({book.quantite_disponible} copies)"
                )
            return f"No, there is no book with ID {book_id}."

        # --- Check for availability question ---
        for book in books:
            if book.titre.lower() in msg:
                if "disponible" in msg or "available" in msg:
                    if book.statut == "disponible":
                        return (
                            f"Yes, '{book.titre}' is available! "
                            f"({book.quantite_disponible} copies in stock)"
                        )
                    return (
                        f"No, '{book.titre}' is currently {book.statut}."
                    )
                return f"'{book.titre}' by {book.auteur} — {book.statut}"

        # --- Recommendation by category ---
        categories = ["roman", "science", "histoire", "informatique", "romantic", "fiction"]
        for cat in categories:
            if cat in msg:
                matching = [b for b in books if cat in b.categorie.lower()]
                if matching:
                    recs = "\n".join(
                        f"   {i+1}. {b.titre} — {b.auteur} ({b.statut})"
                        for i, b in enumerate(matching[:5])
                    )
                    return f"Here are my recommendations:\n{recs}"

        # --- Search by author ---
        for book in books:
            if book.auteur.lower() in msg:
                author_books = [b for b in books if b.auteur.lower() == book.auteur.lower()]
                recs = "\n".join(
                    f"   {i+1}. {b.titre} — {b.statut} ({b.quantite_disponible} copies)"
                    for i, b in enumerate(author_books)
                )
                return f"{book.auteur} is in our catalogue. Here are their works:\n{recs}"

        # --- List everything ---
        if any(w in msg for w in ["all books", "list", "catalogue", "show everything"]):
            if not books:
                return "The library is currently empty."
            lines = "\n".join(
                f"   {b.id_livre}. {b.titre} by {b.auteur} [{b.categorie}]"
                for b in books
            )
            return f"Here is our full catalogue:\n{lines}"

        return (
            "I'm not sure how to answer that. Try asking:\n"
            "- 'Does book ID 1 exist?'\n"
            "- 'Is Les Misérables available?'\n"
            "- 'I want a roman' or 'Recommend a romantic book'\n"
            "- 'Show me books by Victor Hugo'\n"
            "- 'List all books'"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ask(self, user_message: str, user: Optional["User"] = None) -> tuple[str, str]:
        print(f"[ChatService] ask() called with: '{user_message}'")
        print(f"[ChatService] AI_API_KEY set: {bool(settings.AI_API_KEY)}")
        print(f"[ChatService] AI_MODEL: {settings.AI_MODEL}")
        context = self._build_library_context(user)
        print(f"[ChatService] Context length: {len(context)} chars")

        ai_reply = self._ask_ai(user_message, context, user)
        print(f"[ChatService] ai_reply: {ai_reply}")
        if ai_reply:
            return ai_reply, "ai"

        return "Sorry, the AI service is currently unavailable. Please check your API key and try again later.", "error"
