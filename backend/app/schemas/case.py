from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CaseTagCreate(BaseModel):
    tag: str = Field(..., max_length=50)


class CaseMediaCreate(BaseModel):
    media_type: str = Field(..., pattern="^(photo|video)$")
    url: str = Field(..., max_length=500)
    description: Optional[str] = None


class CaseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    symptom: str = Field(..., min_length=10)
    diagnosis: Optional[str] = None
    solution: str = Field(..., min_length=10)
    tools_used: Optional[str] = None
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    tags: List[CaseTagCreate] = []
    media: List[CaseMediaCreate] = []


class CaseResponse(BaseModel):
    id: int
    user_id: int
    title: str
    symptom: str
    diagnosis: Optional[str]
    solution: str
    tools_used: Optional[str]
    difficulty: str
    is_verified: bool
    view_count: int
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []
    media: List[dict] = []

    class Config:
        from_attributes = True
