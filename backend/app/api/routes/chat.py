"""Chat and routing API routes."""
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_csrf
from app.db.database import get_db
from app.db.models import Message, User
from app.schemas.chat import (
    ChatRequest, ChatResponse, ExecuteRequest, ExecuteResponse, RouteRequest, RouteResponse,
)
from app.services.chat_service import ChatService
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/chat", tags=["Chat"])
service = ChatService()


@router.post("", response_model=ChatResponse, dependencies=[Depends(require_csrf)])
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        if request.conversation_id:
            try:
                conversation_uuid = UUID(request.conversation_id)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail="Invalid conversation ID.") from exc
            conversation = ConversationService.get_for_user(db, user, conversation_uuid)
            if conversation is None:
                raise HTTPException(status_code=404, detail="Conversation not found.")
        else:
            conversation = ConversationService.create(db, user, request.prompt[:48] or "New chat")

        history = [
            {"role": message.role, "content": message.content}
            for message in (
                db.query(Message)
                .filter(Message.conversation_id == conversation.id)
                .order_by(Message.created_at.desc(), Message.id.desc())
                .limit(100)
                .all()
            )
            if message.role in {"user", "assistant"}
        ]
        history.reverse()

        result = service.generate_response(
            prompt=request.prompt,
            history=history,
            conversation_id=str(conversation.id),
            user_id=user.id,
        )

        # Persist the exchange only after inference succeeds. The routing and
        # sustainability payload is retained with the assistant message so
        # historical Routing Details remain available after reload.
        db.add(Message(conversation_id=conversation.id, role="user", content=request.prompt))
        db.add(Message(
            conversation_id=conversation.id,
            role="assistant",
            content=result["content"],
            message_metadata=jsonable_encoder(result),
        ))
        if conversation.title == "New chat":
            conversation.title = request.prompt.strip().replace("\n", " ")[:48] or "New chat"
        conversation.updated_at = datetime.now(timezone.utc)
        db.commit()
        return result
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail={"code": "CHAT_REQUEST_FAILED", "message": str(exc)}) from exc


@router.post("/route", response_model=RouteResponse, dependencies=[Depends(require_csrf)])
def route(request: RouteRequest, user: User = Depends(get_current_user)):
    try:
        return service.route(prompt=request.prompt, preset=request.preset)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "ROUTE_REQUEST_FAILED", "message": str(exc)}) from exc


@router.post("/execute", response_model=ExecuteResponse, dependencies=[Depends(require_csrf)])
def execute(request: ExecuteRequest, user: User = Depends(get_current_user)):
    try:
        return service.execute(
            prompt=request.prompt, model=request.model, preset=request.preset,
            ideal_model=request.ideal_model, capability_gap=request.capability_gap,
            ideal_estimated_carbon_g=request.ideal_estimated_carbon_g,
            selected_estimated_carbon_g=request.selected_estimated_carbon_g,
            selected_is_free=request.selected_is_free,
            task_type=request.task_type, fit_score=request.fit_score,
            user_id=user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "EXECUTE_REQUEST_FAILED", "message": str(exc)}) from exc
