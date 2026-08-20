from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import jwt
from pydantic import BaseModel

from app.database import get_db
from app.models import User, AccessRequest
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    require_admin
)

router = APIRouter()


# ============ СХЕМЫ ============
class UserLogin(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: Optional[str] = None
    password: str


class WhitelistLoginRequest(BaseModel):
    telegram_id: int


class AccessRequestCreate(BaseModel):
    email: str
    full_name: str
    message: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    id: int
    username: str
    first_name: str
    last_name: Optional[str]
    email: Optional[str]
    telegram_id: Optional[int]
    is_subscribed: bool
    is_admin: bool
    is_super_admin: bool


# ============ РЕГИСТРАЦИЯ ============
@router.post("/register")
async def register(
        user_data: UserCreate,
        db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    # Проверка email
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    # Проверка username
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username уже занят")

    # Создание пользователя
    hashed = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hashed_password=hashed,
        is_active=True,
        is_subscribed=False,
        is_admin=False,
        is_super_admin=False,
        created_at=datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email,
        "username": new_user.username,
        "first_name": new_user.first_name,
        "message": "Пользователь зарегистрирован"
    }


# ============ ВХОД ПО EMAIL ============
@router.post("/login")
async def login(
        login_data: UserLogin,
        db: Session = Depends(get_db)
):
    """Вход по email и паролю"""
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт деактивирован")

    # Создаём токен
    token = create_access_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        telegram_id=user.telegram_id,
        is_subscribed=user.is_subscribed,
        is_admin=user.is_admin,
        is_super_admin=user.is_super_admin
    )


# ============ ВХОД ПО TELEGRAM ID (БЕЛЫЙ СПИСОК) ============
@router.post("/whitelist-login")
async def whitelist_login(
        request: WhitelistLoginRequest,
        db: Session = Depends(get_db)
):
    """Вход по Telegram ID (только для пользователей из белого списка)"""

    # Ищем пользователя по telegram_id
    user = db.query(User).filter(User.telegram_id == request.telegram_id).first()

    # Если пользователь не найден
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )

    # Проверяем, активен ли пользователь
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт деактивирован"
        )

    # Обновляем время последнего входа
    user.last_login = datetime.utcnow()
    db.commit()

    # Создаём токен
    token = create_access_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        telegram_id=user.telegram_id,
        is_subscribed=user.is_subscribed,
        is_admin=user.is_admin,
        is_super_admin=user.is_super_admin
    )


# ============ ЗАПРОС ДОСТУПА ============
@router.post("/access-request")
async def request_access(
        request: AccessRequestCreate,
        db: Session = Depends(get_db)
):
    """Запрос на доступ в клуб"""

    # Проверяем, не было ли уже заявки
    existing = db.query(AccessRequest).filter(
        AccessRequest.email == request.email,
        AccessRequest.status == "pending"
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Заявка уже отправлена, ожидайте рассмотрения"
        )

    new_request = AccessRequest(
        email=request.email,
        full_name=request.full_name,
        message=request.message,
        status="pending",
        created_at=datetime.utcnow()
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return {
        "id": new_request.id,
        "message": "Заявка отправлена на рассмотрение"
    }


# ============ ПОЛУЧИТЬ ИНФОРМАЦИЮ О ТЕКУЩЕМ ПОЛЬЗОВАТЕЛЕ ============
@router.get("/me")
async def get_current_user(
        current_user: User = Depends(require_admin),  # Используем require_admin для проверки токена
        db: Session = Depends(get_db)
):
    """Получить информацию о текущем пользователе"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "telegram_id": current_user.telegram_id,
        "is_subscribed": current_user.is_subscribed,
        "is_admin": current_user.is_admin,
        "is_super_admin": current_user.is_super_admin
    }