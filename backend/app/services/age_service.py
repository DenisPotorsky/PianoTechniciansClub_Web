from sqlalchemy.orm import Session
from app.models import Brand, SerialRange
from unidecode import unidecode
import re


class AgeService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def normalize_text(text: str) -> str:
        """Нормализация строки: убираем умлауты, приводим к нижнему регистру"""
        return unidecode(text).lower().strip()

    @staticmethod
    def extract_number(text: str) -> int:
        """Извлекает число из строки"""
        numbers = re.findall(r'\d+', text)
        if not numbers:
            raise ValueError("Серийный номер не содержит цифр")
        return int(''.join(numbers))

    async def find_brand(self, brand_name: str, brand_type: str):
        """Поиск бренда с нормализацией"""
        normalized_input = self.normalize_text(brand_name)

        brands = self.db.query(Brand).filter(Brand.type == brand_type).all()

        for brand in brands:
            normalized_brand = self.normalize_text(brand.name)
            if normalized_input in normalized_brand or normalized_brand in normalized_input:
                return brand

        return None

    async def detect_age(self, brand_name: str, brand_type: str, serial_number: str) -> dict:
        brand = await self.find_brand(brand_name, brand_type)

        if not brand:
            return {"error": f"Бренд '{brand_name}' не найден"}

        try:
            serial = self.extract_number(serial_number)
        except ValueError as e:
            return {"error": str(e)}

        serial_range = self.db.query(SerialRange).filter(
            SerialRange.brand_id == brand.id,
            SerialRange.serial_start <= serial,
            SerialRange.serial_end >= serial
        ).first()

        if not serial_range:
            return {"error": f"Серийный номер {serial} не найден для бренда {brand.name}"}

        return {
            "brand": brand.name,
            "country": brand.country,
            "serial_number": serial,
            "year": serial_range.year,
            "info": brand.info
        }