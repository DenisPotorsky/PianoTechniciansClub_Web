from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.database import get_db
from app.models import User, AccessRequest
from app.core.security import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, require_admin
)

router = APIRouter()


# ============ МОДЕЛИ ============
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: Optional[str] = None
    password: str


class WhitelistLoginRequest(BaseModel):
    telegram_id: int


class AccessRequestCreate(BaseModel):
    full_name: str
    email: EmailStr
    message: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    telegram_id: Optional[int]
    email: str
    username: str
    first_name: str
    last_name: Optional[str]
    is_subscribed: bool
    is_admin: bool
    is_super_admin: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ ЭНДПОИНТЫ ============
@router.post("/login")
async def login(
        request: LoginRequest,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт деактивирован")

    # Обновляем время входа
    user.last_login = datetime.utcnow()
    db.commit()

    # Создаём токен
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": user.id,
        "telegram_id": user.telegram_id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_subscribed": user.is_subscribed,
        "is_admin": user.is_admin,
        "is_super_admin": user.is_super_admin,
        "is_active": user.is_active,
        "created_at": user.created_at
    }


@router.post("/whitelist-login")
async def whitelist_login(
        request: WhitelistLoginRequest,
        db: Session = Depends(get_db)
):
    print(f"🔍 Попытка входа по Telegram ID: {request.telegram_id}")

    user = db.query(User).filter(User.telegram_id == request.telegram_id).first()
    if not user:
        print(f"❌ Пользователь с Telegram ID {request.telegram_id} не найден")
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    print(f"✅ Найден пользователь: {user.first_name} {user.last_name}")
    print(f"   is_admin: {user.is_admin}, is_super_admin: {user.is_super_admin}")

    if not user.is_admin and not user.is_super_admin:
        print("❌ Пользователь не в белом списке")
        raise HTTPException(status_code=403, detail="Нет доступа")

    if not user.is_active:
        print("❌ Пользователь не активен")
        raise HTTPException(status_code=403, detail="Аккаунт деактивирован")

    # Обновляем время входа
    user.last_login = datetime.utcnow()
    db.commit()

    # Создаём токен
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": user.id,
        "telegram_id": user.telegram_id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_subscribed": user.is_subscribed,
        "is_admin": user.is_admin,
        "is_super_admin": user.is_super_admin,
        "is_active": user.is_active,
        "created_at": user.created_at
    }


@router.post("/register")
async def register(
        request: RegisterRequest,
        db: Session = Depends(get_db)
):
    # Проверяем, существует ли пользователь
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    existing_username = db.query(User).filter(User.username == request.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")

    # Создаём пользователя
    hashed_password = get_password_hash(request.password)
    user = User(
        email=request.email,
        username=request.username,
        first_name=request.first_name,
        last_name=request.last_name,
        hashed_password=hashed_password,
        is_subscribed=False,
        is_admin=False,
        is_super_admin=False,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Создаём заявку на доступ
    access_request = AccessRequest(
        user_id=user.id,
        email=user.email,
        full_name=f"{user.first_name} {user.last_name or ''}".strip(),
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(access_request)
    db.commit()

    return {"message": "Пользователь создан. Ожидайте подтверждения."}


@router.post("/access-request")
async def create_access_request(
        request: AccessRequestCreate,
        db: Session = Depends(get_db)
):
    # Проверяем, есть ли уже заявка
    existing = db.query(AccessRequest).filter(
        AccessRequest.email == request.email,
        AccessRequest.status == "pending"
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Заявка уже отправлена")

    # Проверяем, есть ли пользователь с таким email
    user = db.query(User).filter(User.email == request.email).first()

    access_request = AccessRequest(
        user_id=user.id if user else None,
        email=request.email,
        full_name=request.full_name,
        message=request.message,
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(access_request)
    db.commit()
    db.refresh(access_request)

    return {"message": "Заявка отправлена"}


@router.get("/me")
async def get_current_user_info(
        current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "telegram_id": current_user.telegram_id,
        "email": current_user.email,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "is_subscribed": current_user.is_subscribed,
        "is_admin": current_user.is_admin,
        "is_super_admin": current_user.is_super_admin,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }