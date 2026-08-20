from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.age_database import get_age_db
from app.services.age_service import AgeService
from typing import Optional

router = APIRouter(prefix="/age", tags=["age"])


class AgeRequest(BaseModel):
    brand_name: str
    brand_type: str
    serial_number: str


class AgeResponse(BaseModel):
    brand: str
    country: str
    serial_number: int
    year: int
    info: Optional[str] = None


@router.post("/detect")
async def detect_age(request: AgeRequest, db: Session = Depends(get_age_db)):
    service = AgeService(db)
    result = await service.detect_age(
        brand_name=request.brand_name,
        brand_type=request.brand_type,
        serial_number=request.serial_number
    )

    if "error" in result:
        return {"error": result["error"]}

    return result