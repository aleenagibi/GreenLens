
import secrets

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.db.models import User
from app.services.auth_service import AuthService


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please sign in to continue.",
        )

    user = AuthService.get_user_for_token(db, token)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session has expired.",
        )

    return user


def require_csrf(request: Request):
    session_token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    header_token = request.headers.get("X-CSRF-Token")

    expected = (
        AuthService.csrf_token(session_token)
        if session_token else ""
    )

    if (
        not expected
        or not header_token
        or not secrets.compare_digest(expected, header_token)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed.",
        )
