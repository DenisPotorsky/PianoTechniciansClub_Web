from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import jwt
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.models import User, AccessRequest, EmailVerification
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    require_admin
)
from app.services.email_service import EmailService

router = APIRouter()


# ============ СХЕМЫ ============
class UserLogin(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: Optional[str] = None
    password: str


class WhitelistLoginRequest(BaseModel):
    telegram_id: int


class AccessRequestCreate(BaseModel):
    email: EmailStr
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
    """Регистрация нового пользователя с отправкой письма для подтверждения email"""

    # Проверка email
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    # Проверка username
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username уже занят")

    # Создание пользователя (неактивный до подтверждения email)
    hashed = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hashed_password=hashed,
        is_active=False,  # Неактивен до подтверждения email
        is_subscribed=False,
        is_admin=False,
        is_super_admin=False,
        created_at=datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Создаём токен подтверждения email
    email_service = EmailService()
    token = email_service.generate_token()

    new_verification = EmailVerification(
        user_id=new_user.id,
        email=new_user.email,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(new_verification)
    db.commit()

    # Отправляем письмо с подтверждением
    try:
        sent = email_service.send_verification_email(new_user.email, new_user.username, token)
        if not sent:
            print(f"⚠️ Письмо не отправлено: {new_user.email}")
    except Exception as e:
        print(f"❌ Ошибка отправки письма: {e}")

    return {
        "id": new_user.id,
        "email": new_user.email,
        "username": new_user.username,
        "first_name": new_user.first_name,
        "message": "Пользователь зарегистрирован. Проверьте почту для подтверждения."
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
        raise HTTPException(status_code=403, detail="Аккаунт не активирован. Проверьте почту для подтверждения.")

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

    user = db.query(User).filter(User.telegram_id == request.telegram_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт деактивирован"
        )

    user.last_login = datetime.utcnow()
    db.commit()

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
@router.post("/access-request")
async def request_access(
        request: AccessRequestCreate,
        db: Session = Depends(get_db)
):
    """Запрос на доступ в клуб"""

    # Проверяем, не было ли уже заявки с таким email
    existing = db.query(AccessRequest).filter(
        AccessRequest.email == request.email,
        AccessRequest.status == "pending"
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Заявка уже отправлена, ожидайте рассмотрения"
        )

    # Создаём новую заявку
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


# ============ ПОДТВЕРЖДЕНИЕ EMAIL ============
@router.post("/send-verification")
async def send_verification(
        email: str,
        db: Session = Depends(get_db)
):
    """Отправить письмо с подтверждением email (повторно)"""

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь с таким email не найден")

    if user.is_active:
        raise HTTPException(status_code=400, detail="Email уже подтверждён")

    # Удаляем старые токены
    old_tokens = db.query(EmailVerification).filter(
        EmailVerification.user_id == user.id,
        EmailVerification.is_used == False
    ).all()
    for token in old_tokens:
        db.delete(token)
    db.commit()

    # Генерируем новый токен
    email_service = EmailService()
    token = email_service.generate_token()

    new_verification = EmailVerification(
        user_id=user.id,
        email=email,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(new_verification)
    db.commit()

    # Отправляем письмо
    sent = email_service.send_verification_email(email, user.username, token)

    if not sent:
        raise HTTPException(status_code=500, detail="Не удалось отправить письмо")

    return {"message": "Письмо с подтверждением отправлено на почту"}


@router.get("/verify-email")
async def verify_email(
        token: str,
        db: Session = Depends(get_db)
):
    """Подтверждение email по токену из письма"""

    verification = db.query(EmailVerification).filter(
        EmailVerification.token == token,
        EmailVerification.is_used == False
    ).first()

    if not verification:
        raise HTTPException(status_code=400, detail="Неверный или уже использованный токен")

    if verification.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Срок действия токена истёк. Запросите новое письмо.")

    # Отмечаем токен как использованный
    verification.is_used = True

    # Активируем пользователя
    user = db.query(User).filter(User.id == verification.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.is_active = True
    db.commit()

    # Отправляем приветственное письмо
    try:
        email_service = EmailService()
        email_service.send_welcome_email(user.email, user.username)
    except Exception as e:
        print(f"⚠️ Ошибка отправки приветствия: {e}")

    return {
        "message": "Email успешно подтверждён! Теперь вы можете войти в систему.",
        "email": user.email,
        "username": user.username
    }


# ============ ВОССТАНОВЛЕНИЕ ПАРОЛЯ ============
@router.post("/request-password-reset")
async def request_password_reset(
        email: str,
        db: Session = Depends(get_db)
):
    """Запрос на сброс пароля (отправка письма со ссылкой)"""

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь с таким email не найден")

    # Удаляем старые токены
    old_tokens = db.query(EmailVerification).filter(
        EmailVerification.user_id == user.id,
        EmailVerification.is_used == False
    ).all()
    for token in old_tokens:
        db.delete(token)
    db.commit()

    # Генерируем токен
    email_service = EmailService()
    token = email_service.generate_token()

    new_verification = EmailVerification(
        user_id=user.id,
        email=email,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(new_verification)
    db.commit()

    # Отправляем письмо
    sent = email_service.send_password_reset_email(email, user.username, token)

    if not sent:
        raise HTTPException(status_code=500, detail="Не удалось отправить письмо")

    return {"message": "Письмо для сброса пароля отправлено на почту"}


@router.post("/reset-password")
async def reset_password(
        token: str,
        new_password: str,
        db: Session = Depends(get_db)
):
    """Сброс пароля по токену из письма"""

    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Пароль должен содержать минимум 6 символов")

    verification = db.query(EmailVerification).filter(
        EmailVerification.token == token,
        EmailVerification.is_used == False
    ).first()

    if not verification:
        raise HTTPException(status_code=400, detail="Неверный или уже использованный токен")

    if verification.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Срок действия токена истёк. Запросите новый сброс.")

    verification.is_used = True

    user = db.query(User).filter(User.id == verification.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.hashed_password = get_password_hash(new_password)
    db.commit()

    return {"message": "Пароль успешно изменён! Теперь вы можете войти с новым паролем."}


# ============ ПОЛУЧИТЬ ИНФОРМАЦИЮ О ТЕКУЩЕМ ПОЛЬЗОВАТЕЛЕ ============
@router.get("/me")
async def get_current_user(
        current_user: User = Depends(require_admin),
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
        "is_super_admin": current_user.is_super_admin,
        "is_active": current_user.is_active
    }