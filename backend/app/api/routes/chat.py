"""Chat and routing API routes."""

from fastapi import APIRouter, HTTPException
from app.schemas.chat import (
    ChatRequest, ChatResponse, ExecuteRequest, ExecuteResponse, RouteRequest, RouteResponse,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])
service = ChatService()


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        return service.generate_response(prompt=request.prompt)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "CHAT_REQUEST_FAILED", "message": str(exc)}) from exc


@router.post("/route", response_model=RouteResponse)
def route(request: RouteRequest):
    try:
        return service.route(prompt=request.prompt, preset=request.preset)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "ROUTE_REQUEST_FAILED", "message": str(exc)}) from exc


@router.post("/execute", response_model=ExecuteResponse)
def execute(request: ExecuteRequest):
    try:
        return service.execute(
            prompt=request.prompt, model=request.model, preset=request.preset,
            ideal_model=request.ideal_model, capability_gap=request.capability_gap,
            ideal_estimated_carbon_g=request.ideal_estimated_carbon_g,
            selected_estimated_carbon_g=request.selected_estimated_carbon_g,
            selected_is_free=request.selected_is_free,
            task_type=request.task_type, fit_score=request.fit_score,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "EXECUTE_REQUEST_FAILED", "message": str(exc)}) from exc
