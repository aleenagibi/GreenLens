"""User-owned conversation history endpoints."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_csrf
from app.db.database import get_db
from app.db.models import Conversation, Message, User
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


class CreateConversationRequest(BaseModel):
    title: str = Field(default="New chat", max_length=255)


class RenameConversationRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class LegacyTurn(BaseModel):
    id: str | None = None
    prompt: str = Field(min_length=1, max_length=100_000)
    ts: str | None = None
    answer: dict | None = None
    error: str | None = None


class LegacyConversation(BaseModel):
    id: str = Field(min_length=1, max_length=128)
    title: str = Field(default="New chat", max_length=255)
    createdAt: str | None = None
    updatedAt: str | None = None
    turns: list[LegacyTurn] = Field(default_factory=list, max_length=200)


class LegacyImportRequest(BaseModel):
    conversations: list[LegacyConversation] = Field(default_factory=list, max_length=30)


@router.get("")
def list_conversations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return {"conversations": [ConversationService.serialize(c) for c in ConversationService.list_for_user(db, user)]}


@router.post("", dependencies=[Depends(require_csrf)])
def create_conversation(payload: CreateConversationRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    conversation = ConversationService.create(db, user, payload.title)
    return {"conversation": ConversationService.serialize(conversation)}


@router.post("/import", dependencies=[Depends(require_csrf)])
def import_legacy_conversations(payload: LegacyImportRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """One-time import of the user's old browser-only chat history; never deletes local data."""
    imported = 0
    for legacy in payload.conversations:
        existing = db.query(Conversation).filter(
            Conversation.user_id == user.id,
            Conversation.legacy_id == legacy.id,
        ).one_or_none()
        if existing is not None:
            continue
        conversation = Conversation(
            user_id=user.id,
            title=legacy.title[:255] or "New chat",
            legacy_id=legacy.id,
        )
        db.add(conversation)
        db.flush()
        for turn in legacy.turns:
            if not turn.answer or not isinstance(turn.answer.get("content"), str):
                continue
            db.add(Message(conversation_id=conversation.id, role="user", content=turn.prompt))
            db.add(Message(
                conversation_id=conversation.id,
                role="assistant",
                content=turn.answer["content"],
                message_metadata={"legacy_answer": turn.answer},
            ))
        imported += 1
    db.commit()
    return {"imported": imported}


@router.get("/{conversation_id}")
def get_conversation(conversation_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    conversation = ConversationService.get_for_user(db, user, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"conversation": ConversationService.serialize(conversation, include_messages=True)}


@router.patch("/{conversation_id}", dependencies=[Depends(require_csrf)])
def rename_conversation(conversation_id: UUID, payload: RenameConversationRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    conversation = ConversationService.get_for_user(db, user, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    conversation.title = payload.title.strip()
    db.commit()
    db.refresh(conversation)
    return {"conversation": ConversationService.serialize(conversation)}


@router.delete("/{conversation_id}", dependencies=[Depends(require_csrf)])
def delete_conversation(conversation_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    conversation = ConversationService.get_for_user(db, user, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    db.delete(conversation)
    db.commit()
    return Response(status_code=204)
