import json
from sqlalchemy.orm import Session
from app.models import Calculation


class CalculationService:
    def __init__(self, db: Session):
        self.db = db

    async def save_calculation(self, user_id: int, winding_type: str, core_diameter: float, total_diameter: float,
                               string_length: float, result_data: dict):
        calculation = Calculation(
            user_id=user_id,
            winding_type=winding_type,
            core_diameter=core_diameter,
            total_diameter=total_diameter,
            string_length=string_length,
            result_data=json.dumps(result_data)
        )
        self.db.add(calculation)
        self.db.commit()
        self.db.refresh(calculation)
        return calculation

    async def get_user_calculations(self, user_id: int, limit: int = 50, skip: int = 0):
        return self.db.query(Calculation).filter(Calculation.user_id == user_id).order_by(
            Calculation.created_at.desc()).offset(skip).limit(limit).all()

    async def delete_calculation(self, calculation_id: int, user_id: int):
        calc = self.db.query(Calculation).filter(Calculation.id == calculation_id,
                                                 Calculation.user_id == user_id).first()
        if calc:
            self.db.delete(calc)
            self.db.commit()
            return True
        return False