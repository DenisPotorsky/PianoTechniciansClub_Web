from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import secrets

from app.database import get_db
from app.models import User, AccessRequest, EmailVerification
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    require_admin
)

# УБРАЛИ ИМПОРТ EMAIL ФУНКЦИЙ, ЧТОБЫ НЕ ПАДАЛО
# from app.utils.email import send_verification_email, send_approval_email

router = APIRouter()


# === СХЕМЫ ===

class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    id: int
    email: str
    username: str
    first_name: str
    last_name: Optional[str]
    phone: Optional[str]
    city: Optional[str]
    telegram_id: Optional[int]
    is_subscribed: bool
    is_approved: bool
    is_admin: bool
    is_super_admin: bool
    created_at: datetime


class RequestAccessSchema(BaseModel):
    full_name: str
    email: EmailStr
    message: Optional[str] = None


class WhitelistLoginRequest(BaseModel):
    telegram_id: int


# === ЭНДПОИНТЫ ===

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == func.lower(data.email)).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт деактивирован")

    user.last_login = datetime.utcnow()
    db.commit()

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "city": user.city,
        "telegram_id": user.telegram_id,
        "is_subscribed": user.is_subscribed,
        "is_approved": user.is_approved,
        "is_admin": user.is_admin,
        "is_super_admin": user.is_super_admin,
        "created_at": user.created_at
    }


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Получение данных текущего пользователя"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone": current_user.phone,
        "city": current_user.city,
        "telegram_id": current_user.telegram_id,
        "is_subscribed": current_user.is_subscribed,
        "is_approved": current_user.is_approved,
        "is_admin": current_user.is_admin,
        "is_super_admin": current_user.is_super_admin,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }


@router.post("/request-access")
async def request_access(
        data: RequestAccessSchema,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(func.lower(User.email) == func.lower(data.email)).first()
    if existing_user:
        if existing_user.is_approved or existing_user.is_subscribed:
            raise HTTPException(status_code=400, detail="Вы уже зарегистрированы")
        existing_req = db.query(AccessRequest).filter(
            AccessRequest.email == data.email,
            AccessRequest.status == "pending"
        ).first()
        if existing_req:
            raise HTTPException(status_code=400, detail="Заявка уже на рассмотрении")

    new_request = AccessRequest(
        email=data.email,
        full_name=data.full_name,
        message=data.message,
        status="pending"
    )
    db.add(new_request)
    db.commit()

    return {"message": "Заявка отправлена. Ожидайте подтверждения."}


@router.post("/whitelist-login", response_model=TokenResponse)
async def whitelist_login(data: WhitelistLoginRequest, db: Session = Depends(get_db)):
    """Вход по Telegram ID"""
    user = db.query(User).filter(User.telegram_id == data.telegram_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь с таким Telegram ID не найден")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт деактивирован")

    if not user.is_approved and not user.is_subscribed:
        raise HTTPException(status_code=403, detail="Доступ запрещен. Ожидает одобрения.")

    user.last_login = datetime.utcnow()
    db.commit()

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "city": user.city,
        "telegram_id": user.telegram_id,
        "is_subscribed": user.is_subscribed,
        "is_approved": user.is_approved,
        "is_admin": user.is_admin,
        "is_super_admin": user.is_super_admin,
        "created_at": user.created_at
    }