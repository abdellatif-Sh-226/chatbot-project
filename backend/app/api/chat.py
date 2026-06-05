"""
Chatbot API route.

Accepts a natural-language question from the user and
returns an AI-generated answer based on the library data.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import ChatService
from app.core.dependencies import get_current_user
from app.models.book import User

router = APIRouter(prefix="/chat", tags=["Chatbot"])


@router.post("/", response_model=ChatResponse)
def chat(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message to the AI library chatbot and get a reply."""
    service = ChatService(db)
    reply, source = service.ask(data.message, current_user)
    return ChatResponse(reply=reply, source=source)
