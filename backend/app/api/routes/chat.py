"""
Chat API Routes
"""

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from fastapi import APIRouter

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

    response = service.generate_response(
        prompt=request.prompt,
    )

    return response