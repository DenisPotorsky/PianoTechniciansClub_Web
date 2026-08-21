from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
import re
from unidecode import unidecode

from app.database import get_db
from app.models import User, Brand, SerialRange
from app.core.security import require_member

router = APIRouter()


class AgeDetectRequest(BaseModel):
    brand_name: str
    brand_type: str = "foreign"  # По умолчанию иностранные
    serial_number: str


def normalize_text(text: str) -> str:
    """Нормализация текста: убираем умляуты, приводим к нижнему регистру"""
    if not text:
        return ""
    text = unidecode(text)
    return text.lower().strip()


@router.post("/detect")
async def detect_age(
        data: AgeDetectRequest,
        current_user: User = Depends(require_member),
        db: Session = Depends(get_db)
):
    """Определение возраста инструмента по бренду и серийному номеру"""

    # 1. Нормализуем введённое название
    search_normalized = normalize_text(data.brand_name)

    # 2. Ищем бренд (сначала в указанном типе, потом во всех)
    brand = None

    # Пробуем найти точное совпадение (регистронезависимо, с умляутами)
    # Получаем все бренды
    all_brands = db.query(Brand).all()

    # Ищем по нормализованному названию
    for b in all_brands:
        b_normalized = normalize_text(b.name)
        # Проверяем несколько вариантов совпадения
        if (search_normalized == b_normalized or
                search_normalized in b_normalized or
                b_normalized in search_normalized):
            brand = b
            break

    # 3. Если не нашли — ищем по частичному совпадению через LIKE
    if not brand:
        brand = db.query(Brand).filter(
            func.lower(Brand.name).contains(search_normalized)
        ).first()

    # 4. Если всё равно не нашли — возвращаем ошибку с подсказкой
    if not brand:
        # Ищем похожие бренды
        similar_brands = []
        for b in all_brands:
            b_normalized = normalize_text(b.name)
            if search_normalized[:3] in b_normalized:
                similar_brands.append(b.name)

        similar_brands = list(set(similar_brands))[:5]

        if similar_brands:
            raise HTTPException(
                status_code=404,
                detail=f"Бренд '{data.brand_name}' не найден. Возможно, вы имели в виду: {', '.join(similar_brands)}"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Бренд '{data.brand_name}' не найден в базе. Проверьте правильность написания."
            )

    # 5. Парсим серийный номер
    serial_clean = re.sub(r'[^0-9]', '', data.serial_number)

    if not serial_clean:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат серийного номера (должен содержать цифры)"
        )

    serial_int = int(serial_clean)

    # 6. Ищем диапазон серийных номеров
    range_data = db.query(SerialRange).filter(
        SerialRange.brand_id == brand.id,
        SerialRange.serial_start <= serial_int,
        SerialRange.serial_end >= serial_int
    ).first()

    # 7. Если диапазон не найден — ищем ближайший
    if not range_data:
        nearest = db.query(SerialRange).filter(
            SerialRange.brand_id == brand.id
        ).order_by(SerialRange.serial_start).first()

        if nearest:
            if serial_int < nearest.serial_start:
                return {
                    "brand": brand.name,
                    "country": brand.country,
                    "serial_number": data.serial_number,
                    "year": f"До {nearest.year}",
                    "info": f"Серийный номер меньше минимального ({nearest.serial_start})"
                }
            else:
                return {
                    "brand": brand.name,
                    "country": brand.country,
                    "serial_number": data.serial_number,
                    "year": f"~{nearest.year}",
                    "info": f"Ближайший диапазон: {nearest.serial_start}-{nearest.serial_end} ({nearest.year})"
                }
        else:
            return {
                "brand": brand.name,
                "country": brand.country,
                "serial_number": data.serial_number,
                "year": "Неизвестно",
                "info": f"Нет данных о серийных номерах для {brand.name}"
            }

    # 8. Всё найдено — возвращаем результат
    return {
        "brand": brand.name,
        "country": brand.country,
        "serial_number": data.serial_number,
        "year": range_data.year,
        "info": f"Год выпуска: {range_data.year} (номера {range_data.serial_start}-{range_data.serial_end})"
    }


@router.get("/brands")
async def get_brands(
        current_user: User = Depends(require_member),
        db: Session = Depends(get_db)
):
    """Получить список всех брендов"""
    brands = db.query(Brand).all()
    return [
        {
            "id": b.id,
            "name": b.name,
            "country": b.country,
            "type": b.type
        }
        for b in brands
    ]


@router.get("/suggest")
async def suggest_brands(
        query: str,
        current_user: User = Depends(require_member),
        db: Session = Depends(get_db)
):
    """Поиск брендов по подстроке (для автодополнения)"""
    if not query or len(query) < 1:
        return []

    search_normalized = normalize_text(query)
    results = []

    brands = db.query(Brand).all()
    for brand in brands:
        brand_normalized = normalize_text(brand.name)
        if search_normalized in brand_normalized:
            results.append({
                "name": brand.name,
                "country": brand.country,
                "type": brand.type
            })

    return results[:10]