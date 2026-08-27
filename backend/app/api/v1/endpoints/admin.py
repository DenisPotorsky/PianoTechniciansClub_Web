from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from app.database import get_db
from app.models import User, AccessRequest, Brand, SerialRange
from app.core.security import require_admin, require_super_admin, get_password_hash

router = APIRouter()


# ============ СТАТИСТИКА ============
@router.get("/stats")
async def get_stats(
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    subscribed_users = db.query(User).filter(User.is_subscribed == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    pending_requests = db.query(AccessRequest).filter(AccessRequest.status == "pending").count()

    return {
        "total_users": total_users,
        "subscribed_users": subscribed_users,
        "admin_users": admin_users,
        "pending_requests": pending_requests,
        "total_calculations": 0
    }


# ============ ПОЛЬЗОВАТЕЛИ ============
@router.get("/users")
async def get_users(
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return [{
        "id": u.id,
        "telegram_id": u.telegram_id,
        "username": u.username,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "email": u.email,
        "is_subscribed": u.is_subscribed,
        "is_admin": u.is_admin,
        "is_super_admin": u.is_super_admin,
        "created_at": u.created_at
    } for u in users]


@router.put("/users/{user_id}")
async def update_user(
        user_id: int,
        user_data: dict,
        current_user: User = Depends(require_super_admin),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    for key, value in user_data.items():
        if hasattr(user, key) and value is not None:
            setattr(user, key, value)

    db.commit()
    return {"message": "Пользователь обновлён"}


@router.delete("/users/{user_id}")
async def delete_user(
        user_id: int,
        current_user: User = Depends(require_super_admin),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.is_super_admin:
        raise HTTPException(status_code=403, detail="Нельзя удалить супер-админа")

    db.delete(user)
    db.commit()
    return {"message": "Пользователь удалён"}


# ============ БЕЛЫЙ СПИСОК ============
@router.get("/whitelist")
async def get_whitelist(
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    admins = db.query(User).filter(
        (User.is_admin == True) | (User.is_super_admin == True)
    ).all()

    return [{
        "id": a.id,
        "telegram_id": a.telegram_id,
        "username": a.username,
        "first_name": a.first_name,
        "last_name": a.last_name,
        "is_admin": a.is_admin,
        "is_super_admin": a.is_super_admin
    } for a in admins]


@router.post("/whitelist/add")
async def add_to_whitelist(
        telegram_id: int,
        current_user: User = Depends(require_super_admin),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.is_admin = True
    db.commit()
    return {"message": "Пользователь добавлен в белый список"}


@router.post("/whitelist/remove")
async def remove_from_whitelist(
        telegram_id: int,
        current_user: User = Depends(require_super_admin),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.is_super_admin:
        raise HTTPException(status_code=403, detail="Нельзя удалить супер-админа")

    user.is_admin = False
    db.commit()
    return {"message": "Пользователь удалён из белого списка"}


# ============ ЗАЯВКИ ============
@router.get("/requests")
async def get_requests(
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    requests = db.query(AccessRequest).order_by(AccessRequest.created_at.desc()).all()
    return [{
        "id": r.id,
        "full_name": r.full_name,
        "email": r.email,
        "message": r.message,
        "status": r.status,
        "created_at": r.created_at
    } for r in requests]


@router.post("/requests/{request_id}/approve")
async def approve_request(
        request_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    if request.status != "pending":
        raise HTTPException(status_code=400, detail="Заявка уже обработана")

    # Обновляем заявку
    request.status = "approved"
    request.processed_by = current_user.id
    request.processed_at = datetime.utcnow()

    # Создаём пользователя
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        temp_password = secrets.token_urlsafe(10)[:64]
        user = User(
            email=request.email,
            username=request.full_name.lower().replace(" ", "_"),
            first_name=request.full_name,
            hashed_password=get_password_hash(temp_password),
            is_subscribed=True,
            is_active=True,
            is_admin=False,
            is_super_admin=False,
            created_at=datetime.utcnow()
        )
        db.add(user)
        print(f"✅ Создан пользователь: {user.email}")
    else:
        temp_password = None
        user.is_subscribed = True
        user.is_active = True
        print(f"✅ Обновлён пользователь: {user.email}")

    # ===== ОТПРАВКА ПИСЬМА С ПАРОЛЕМ (ЕСЛИ ПОЛЬЗОВАТЕЛЬ НОВЫЙ) =====
    if temp_password:
        try:
            smtp_user = os.getenv("SMTP_USER")
            smtp_password = os.getenv("SMTP_PASSWORD")
            smtp_host = os.getenv("SMTP_HOST")
            smtp_port = int(os.getenv("SMTP_PORT", 587))
            frontend_url = os.getenv("APP_URL", "http://localhost:3000")

            if not all([smtp_user, smtp_password, smtp_host]):
                print("⚠️ SMTP не настроен. Письмо не отправлено.")
            else:
                subject = "🎹 Ваш доступ в PianoTechniciansClub"
                html = f"""
                <html>
                <body>
                    <h2>Добро пожаловать в PianoTechniciansClub!</h2>
                    <p>Ваша заявка одобрена.</p>
                    <p><b>Ваш email:</b> {user.email}</p>
                    <p><b>Временный пароль:</b> {temp_password}</p>
                    <p><b>Войти:</b> <a href="{frontend_url}/login">Нажмите сюда</a></p>
                    <p>Рекомендуем сменить пароль после первого входа.</p>
                </body>
                </html>
                """

                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = smtp_user
                msg["To"] = user.email
                msg.attach(MIMEText(html, "html"))

                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    server.sendmail(smtp_user, user.email, msg.as_string())

                print(f"📧 Пароль отправлен на {user.email}")
        except Exception as e:
            print(f"⚠️ Ошибка отправки письма пользователю: {e}")

    db.commit()
    return {"message": "Заявка одобрена, пользователь создан"}


@router.post("/requests/{request_id}/reject")
async def reject_request(
        request_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    if request.status != "pending":
        raise HTTPException(status_code=400, detail="Заявка уже обработана")

    request.status = "rejected"
    request.processed_by = current_user.id
    request.processed_at = datetime.utcnow()

    db.commit()
    return {"message": "Заявка отклонена"}


# ============ БРЕНДЫ ============
@router.get("/brands")
async def get_brands_admin(
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    brands = db.query(Brand).all()
    return [{
        "id": b.id,
        "name": b.name,
        "country": b.country,
        "type": b.type,
        "info": b.info,
        "ranges_count": len(b.serial_ranges) if b.serial_ranges else 0
    } for b in brands]


@router.post("/brands")
async def create_brand(
        brand_data: dict,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    new_brand = Brand(
        name=brand_data["name"],
        country=brand_data["country"],
        type=brand_data["type"],
        info=brand_data.get("info")
    )
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    return {"message": "Бренд создан", "id": new_brand.id}


@router.post("/brands/{brand_id}/ranges")
async def add_range(
        brand_id: int,
        range_data: dict,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Бренд не найден")

    new_range = SerialRange(
        brand_id=brand_id,
        serial_start=range_data["serial_start"],
        serial_end=range_data["serial_end"],
        year=range_data["year"]
    )
    db.add(new_range)
    db.commit()
    return {"message": "Диапазон добавлен"}


@router.delete("/brands/{brand_id}")
async def delete_brand(
        brand_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Бренд не найден")

    db.delete(brand)
    db.commit()
    return {"message": "Бренд удалён"}