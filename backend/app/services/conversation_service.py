"""Conversation persistence with mandatory user ownership scoping."""
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.models import Conversation, Message, User


class ConversationService:
    @staticmethod
    def list_for_user(db: Session, user: User) -> list[Conversation]:
        return (
            db.query(Conversation)
            .filter(Conversation.user_id == user.id)
            .order_by(Conversation.updated_at.desc())
            .all()
        )

    @staticmethod
    def get_for_user(db: Session, user: User, conversation_id: UUID) -> Conversation | None:
        return db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id,
        ).one_or_none()

    @staticmethod
    def create(db: Session, user: User, title: str = "New chat") -> Conversation:
        conversation = Conversation(user_id=user.id, title=title[:255] or "New chat")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def serialize(conversation: Conversation, include_messages: bool = False) -> dict:
        result = {
            "id": str(conversation.id),
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
        }
        if include_messages:
            result["messages"] = [
                {
                    "id": str(message.id),
                    "role": message.role,
                    "content": message.content,
                    "metadata": message.message_metadata,
                    "created_at": message.created_at.isoformat(),
                }
                for message in conversation.messages
            ]
        return result
