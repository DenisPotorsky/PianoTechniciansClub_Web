from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.calculator import StringCalculator
from app.services.calculation_service import CalculationService

router = APIRouter(prefix="/calculator", tags=["calculator"])


class CalculationRequest(BaseModel):
    user_id: int
    winding_type: str
    core_diameter: float
    total_diameter: float
    string_length: float


class CalculationResponse(BaseModel):
    result: dict
    saved: bool = True


@router.post("/calculate", response_model=CalculationResponse)
async def calculate_string(request: CalculationRequest, db: Session = Depends(get_db)):
    result = StringCalculator.calculate(
        winding_type=request.winding_type,
        core_diameter=request.core_diameter,
        total_diameter=request.total_diameter,
        string_length=request.string_length
    )

    calculation_service = CalculationService(db)
    await calculation_service.save_calculation(
        user_id=request.user_id,
        winding_type=request.winding_type,
        core_diameter=request.core_diameter,
        total_diameter=request.total_diameter,
        string_length=request.string_length,
        result_data=result
    )

    return CalculationResponse(result=result)


@router.get("/history/{user_id}")
async def get_history(user_id: int, limit: int = 50, skip: int = 0, db: Session = Depends(get_db)):
    calculation_service = CalculationService(db)
    calculations = await calculation_service.get_user_calculations(user_id, limit, skip)
    return [
        {
            "id": calc.id,
            "winding_type": calc.winding_type,
            "core_diameter": calc.core_diameter,
            "total_diameter": calc.total_diameter,
            "string_length": calc.string_length,
            "result": calc.result_data,
            "created_at": calc.created_at.isoformat()
        }
        for calc in calculations
    ]


@router.delete("/history/{calculation_id}")
async def delete_calculation(calculation_id: int, user_id: int, db: Session = Depends(get_db)):
    calculation_service = CalculationService(db)
    deleted = await calculation_service.delete_calculation(calculation_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Расчет не найден")
    return {"message": "Расчет удален"}