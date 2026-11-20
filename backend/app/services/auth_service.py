
"""Email/password authentication and secure session management."""

import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta, timezone

from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import User, UserSession


class AuthenticationError(Exception):
    pass


password_hash = PasswordHash.recommended()


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:

    @staticmethod
    def normalise_email(email: str) -> str:
        value = email.strip().lower()

        if len(value) > 320 or not re.fullmatch(
            r"[^\s@]+@[^\s@]+\.[^\s@]+", value
        ):
            raise AuthenticationError("Enter a valid email address.")

        return value

    @staticmethod
    def validate_password(password: str):
        if len(password) < 8:
            raise AuthenticationError(
                "Password must contain at least 8 characters."
            )

        if len(password) > 128:
            raise AuthenticationError(
                "Password must be 128 characters or fewer."
            )

    @classmethod
    def signup(cls, db: Session, name: str, email: str, password: str):
        clean_name = name.strip()

        if not clean_name or len(clean_name) > 255:
            raise AuthenticationError("Enter a valid name.")

        clean_email = cls.normalise_email(email)
        cls.validate_password(password)

        existing = (
            db.query(User)
            .filter(User.email == clean_email)
            .one_or_none()
        )

        if existing:
            raise AuthenticationError(
                "An account with this email already exists."
            )

        user = User(
            email=clean_email,
            name=clean_name,
            password_hash=password_hash.hash(password),
            email_verified=False,
        )

        return cls.create_session(db, user)

    @classmethod
    def login(cls, db: Session, email: str, password: str):
        clean_email = cls.normalise_email(email)

        user = (
            db.query(User)
            .filter(User.email == clean_email)
            .one_or_none()
        )

        if (
            user is None
            or not user.password_hash
            or not password_hash.verify(password, user.password_hash)
        ):
            raise AuthenticationError("Incorrect email or password.")

        return cls.create_session(db, user)

    @staticmethod
    def create_session(db: Session, user: User):
        token = secrets.token_urlsafe(48)

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.SESSION_MAX_AGE_DAYS
        )

        db.add(user)

        db.add(
            UserSession(
                user=user,
                token_hash=hash_token(token),
                expires_at=expires_at,
            )
        )

        db.commit()
        db.refresh(user)

        return user, token

    @staticmethod
    def csrf_token(token: str) -> str:
        secret = settings.SESSION_SECRET.encode("utf-8")

        return hmac.new(
            secret,
            token.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def get_user_for_token(db: Session, token: str):
        session = (
            db.query(UserSession)
            .filter(
                UserSession.token_hash == hash_token(token),
                UserSession.revoked_at.is_(None),
                UserSession.expires_at > datetime.now(timezone.utc),
            )
            .one_or_none()
        )

        if session is None:
            return None

        session.last_used_at = datetime.now(timezone.utc)
        db.commit()

        return db.get(User, session.user_id)

    @staticmethod
    def revoke(db: Session, token: str):
        session = (
            db.query(UserSession)
            .filter(
                UserSession.token_hash == hash_token(token),
                UserSession.revoked_at.is_(None),
            )
            .one_or_none()
        )

        if session:
            session.revoked_at = datetime.now(timezone.utc)
            db.commit()
