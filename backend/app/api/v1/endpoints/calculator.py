from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from app.database import get_db
from app.models import User, Calculation
from app.core.security import require_member
from app.calculator import StringCalculator

router = APIRouter()


class CalculateRequest(BaseModel):
    winding_type: str  # 'single' или 'double'
    core_diameter: float
    total_diameter: float
    winding_length: float
    ratio: float = 2.5
    end_allowance: float = 60.0


@router.post("/calculate")
async def calculate(
        data: CalculateRequest,
        current_user: User = Depends(require_member),
        db: Session = Depends(get_db)
):
    """Расчёт параметров меди для изготовления басовой струны"""
    try:
        result = StringCalculator.calculate(
            winding_type=data.winding_type,
            core_diameter=data.core_diameter,
            total_diameter=data.total_diameter,
            winding_length=data.winding_length,
            ratio=data.ratio,
            end_allowance=data.end_allowance
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    calculation = Calculation(
        user_id=current_user.id,
        winding_type=data.winding_type,
        core_diameter=data.core_diameter,
        total_diameter=data.total_diameter,
        string_length=data.winding_length,
        result_data=json.dumps({
            "input": {
                "ratio": data.ratio,
                "end_allowance": data.end_allowance
            },
            "result": result
        }, ensure_ascii=False)
    )
    db.add(calculation)
    db.commit()

    return {"result": result}


from typing import List


# ... (существующий код) ...

@router.get("/history", response_model=List[dict])
async def get_calculation_history(
        current_user: User = Depends(require_member),
        db: Session = Depends(get_db)
):
    """Получить историю расчетов текущего пользователя"""
    calculations = db.query(Calculation).filter(
        Calculation.user_id == current_user.id
    ).order_by(Calculation.created_at.desc()).limit(10).all()

    return [
        {
            "id": calc.id,
            "winding_type": calc.winding_type,
            "core_diameter": calc.core_diameter,
            "total_diameter": calc.total_diameter,
            "string_length": calc.string_length,
            "result_data": calc.result_data,  # Это строка, распарсим на фронте
            "created_at": calc.created_at.isoformat()
        }
        for calc in calculations
    ]