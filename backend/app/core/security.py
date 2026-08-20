from datetime import datetime, timedelta
import hashlib
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()


def get_password_hash(password: str) -> str:
    """Хеширует пароль с использованием SHA256"""
    salt = "piano_club_salt_2026"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль"""
    return get_password_hash(plain_password) == hashed_password


def create_access_token(data: dict) -> str:
    """Создает JWT токен"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    """Получает текущего пользователя из токена"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    return user


# ============ ПРОВЕРКА РОЛЕЙ ============
async def require_any(current_user: User = Depends(get_current_user)):
    """Требуется любой авторизованный пользователь"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация"
        )
    return current_user


async def require_member(current_user: User = Depends(get_current_user)):
    """Требуется подписанный пользователь (белый список)"""
    if not current_user.is_subscribed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ только для участников клуба"
        )
    return current_user


async def require_admin(current_user: User = Depends(get_current_user)):
    """Требуется администратор"""
    if not (current_user.is_admin or current_user.is_super_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    return current_user


async def require_super_admin(current_user: User = Depends(get_current_user)):
    """Требуется супер-администратор"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    return current_user