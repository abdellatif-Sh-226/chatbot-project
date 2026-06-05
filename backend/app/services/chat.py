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
from app.models.book import Book
from app.config import settings


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

    def _build_library_context(self) -> str:
        books: List[Book] = self.db.query(Book).order_by(Book.id_livre).all()
        if not books:
            return "The library is currently empty."

        lines = []
        for b in books:
            lines.append(
                f"- ID {b.id_livre}: '{b.titre}' by {b.auteur} "
                f"[{b.categorie}, {b.annee_publication or 'N/A'}] "
                f"Status: {b.statut}, Copies available: {b.quantite_disponible}"
            )
        return "\n".join(lines)

    def _ask_ai(self, user_message: str, context: str) -> Optional[str]:
        model_name = self._get_gemini_model()
        if not model_name:
            return None

        system_prompt = (
            "You are a library assistant named SmartLib. "
            "Only introduce yourself if the user greets you. "
            "Otherwise answer briefly and naturally. "
            "Use ONLY the book data below.\n\n"
            f"Library catalogue:\n{context}"
        )

        try:
            response = self._client.models.generate_content(
                model=model_name,
                contents=[system_prompt, user_message],
                config={"temperature": 0.3, "max_output_tokens": 512},
            )
            return response.text.strip()
        except Exception as e:
            print(f"[ChatService] Gemini generate_content failed: {e}")
            return None

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

    def ask(self, user_message: str) -> tuple[str, str]:
        print(f"[ChatService] ask() called with: '{user_message}'")
        print(f"[ChatService] AI_API_KEY set: {bool(settings.AI_API_KEY)}")
        print(f"[ChatService] AI_MODEL: {settings.AI_MODEL}")
        context = self._build_library_context()
        print(f"[ChatService] Context length: {len(context)} chars")

        ai_reply = self._ask_ai(user_message, context)
        print(f"[ChatService] ai_reply: {ai_reply}")
        if ai_reply:
            return ai_reply, "ai"

        reply = self._fallback_reply(user_message)
        print(f"[ChatService] Using fallback: '{reply[:50]}...'")
        return reply, "fallback"
