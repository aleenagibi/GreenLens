"""
Chat API Routes
"""

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

service = ChatService()


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):

    try:
        response = service.generate_response(
            prompt=request.prompt,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "CHAT_REQUEST_FAILED",
                "message": str(exc),
            },
        ) from exc

    return response