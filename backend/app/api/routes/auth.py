
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_csrf
from app.core.config import settings
from app.db.database import get_db
from app.db.models import User
from app.services.auth_service import AuthService, AuthenticationError

router = APIRouter(prefix="/auth", tags=["Authentication"])


class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1, max_length=128)


def user_payload(user: User):
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "picture_url": user.picture_url,
        "email_verified": user.email_verified,
    }


def set_auth_cookies(response: Response, token: str):
    response.set_cookie(
        settings.SESSION_COOKIE_NAME,
        token,
        max_age=settings.SESSION_MAX_AGE_DAYS * 86400,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )

    return AuthService.csrf_token(token)


def auth_response(user: User, token: str, response: Response):
    csrf = set_auth_cookies(response, token)

    return {
        "user": user_payload(user),
        "csrf_token": csrf,
    }


@router.post("/signup")
def signup(
    payload: SignupRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        user, token = AuthService.signup(
            db,
            payload.name,
            payload.email,
            payload.password,
        )
    except AuthenticationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return auth_response(user, token, response)


@router.post("/login")
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        user, token = AuthService.login(
            db,
            payload.email,
            payload.password,
        )
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    return auth_response(user, token, response)


@router.get("/me")
def current_user(
    request: Request,
    user: User = Depends(get_current_user),
):
    token = request.cookies.get(settings.SESSION_COOKIE_NAME, "")

    return {
        "user": user_payload(user),
        "csrf_token": AuthService.csrf_token(token),
    }


@router.post("/logout", dependencies=[Depends(require_csrf)])
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)

    if token:
        AuthService.revoke(db, token)

    response.delete_cookie(
        settings.SESSION_COOKIE_NAME,
        path="/",
        secure=settings.COOKIE_SECURE,
        httponly=True,
        samesite=settings.COOKIE_SAMESITE,
    )

    return {"success": True}
