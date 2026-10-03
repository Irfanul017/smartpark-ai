"""Password hashing, JWT handling, and role dependencies."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Callable

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserRegister

JWT_SECRET = os.getenv("SMARTPARK_JWT_SECRET", "smartpark-ai-development-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 8
bearer_scheme = HTTPBearer(auto_error=False)


class AuthService:
    def register(self, db: Session, payload: UserRegister) -> User:
        user = User(
            username=payload.username,
            email=payload.email.casefold(),
            password_hash=self.hash_password(payload.password),
            role=payload.role,
        )
        db.add(user)
        try:
            db.commit()
        except IntegrityError as error:
            db.rollback()
            raise ValueError("Username or email is already registered.") from error
        db.refresh(user)
        return user

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    def authenticate(self, db: Session, username: str, password: str) -> User | None:
        user = db.scalar(select(User).where(User.username == username))
        if user is None or not self.verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def create_token(user: User) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
        return jwt.encode({"sub": str(user.id), "role": user.role, "exp": expires_at}, JWT_SECRET, algorithm=JWT_ALGORITHM)


auth_service = AuthService()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication is required.")
    try:
        claims = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(claims["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token.") from error
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists.")
    return user


def require_roles(*roles: str) -> Callable[[User], User]:
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role permissions.")
        return current_user

    return role_dependency
