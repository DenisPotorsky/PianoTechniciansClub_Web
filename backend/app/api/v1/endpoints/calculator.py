from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models import User, Calculation
from app.core.security import require_member

router = APIRouter()


class CalculateRequest(BaseModel):
    user_id: int
    winding_type: str  # 'single' или 'double'
    core_diameter: float
    total_diameter: float
    string_length: float


@router.post("/calculate")
async def calculate(
        data: CalculateRequest,
        current_user: User = Depends(require_member),
        db: Session = Depends(get_db)
):
    """Расчёт параметров басовых струн"""

    # Расчёт для одиночной навивки
    if data.winding_type == 'single':
        copper_diameter = (data.total_diameter - data.core_diameter) / 2
        copper_length = data.string_length * 1.1  # Примерный коэффициент

        result = {
            "copper_diameter": round(copper_diameter, 2),
            "copper_length": round(copper_length, 2),
            # "weight_estimate": round(copper_length * 0.008, 2)  # Примерный вес
        }

    # Расчёт для двойной навивки
    else:
        primary_copper = (data.total_diameter - data.core_diameter) / 3
        secondary_copper = (data.total_diameter - data.core_diameter) / 4

        result = {
            "primary_copper_diameter": round(primary_copper, 2),
            "secondary_copper_diameter": round(secondary_copper, 2),
            "primary_copper_length": round(data.string_length * 0.6, 2),
            "secondary_copper_length": round(data.string_length * 0.5, 2),
            # "weight_estimate": round(data.string_length * 0.012, 2)
        }

    # Сохраняем в историю
    calculation = Calculation(
        user_id=data.user_id,
        winding_type=data.winding_type,
        core_diameter=data.core_diameter,
        total_diameter=data.total_diameter,
        string_length=data.string_length,
        result_data=str(result)
    )
    db.add(calculation)
    db.commit()

    return {"result": result}