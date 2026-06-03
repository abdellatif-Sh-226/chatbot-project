"""
Pydantic schemas for the AI chatbot.

Defines the request format (user question) and
response format (chatbot answer).
"""

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming user message to the chatbot."""

    message: str = Field(..., min_length=1, max_length=2000, description="User's natural-language question")


class ChatResponse(BaseModel):
    """Chatbot reply returned to the user."""

    reply: str = Field(..., description="AI-generated answer based on library data")
    source: str = Field("ai", description="Source of the reply: 'ai' or 'fallback'")
