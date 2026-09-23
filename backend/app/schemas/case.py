from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ===== Symptom =====
class SymptomCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class SymptomResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    description: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True


# ===== Tag =====
class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=100)

class TagResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True


# ===== Solution =====
class SolutionCreate(BaseModel):
    text: str = Field(..., min_length=10)
    tools_used: Optional[str] = None
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")

class SolutionUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=10)
    tools_used: Optional[str] = None
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    is_best: Optional[bool] = None

class SolutionResponse(BaseModel):
    id: int
    case_id: int
    author_id: int
    author_name: Optional[str] = None
    text: str
    tools_used: Optional[str]
    difficulty: str
    is_best: bool
    upvotes: int
    downvotes: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# ===== CaseMedia =====
class CaseMediaCreate(BaseModel):
    media_type: str = Field(..., pattern="^(photo|video)$")
    url: str = Field(..., max_length=500)
    description: Optional[str] = None

class CaseMediaResponse(BaseModel):
    id: int
    media_type: str
    url: str
    description: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True


# ===== CaseVersion =====
class CaseVersionResponse(BaseModel):
    id: int
    version: int
    title: str
    symptom: str
    diagnosis: Optional[str]
    solution: Optional[str]
    tools_used: Optional[str]
    difficulty: str
    edited_by: int
    change_summary: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True


# ===== Case =====
class CaseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    symptom_text: Optional[str] = None  # свободный текст для поиска
    symptom_ids: List[int] = []  # привязка к справочнику симптомов
    tag_ids: List[int] = []  # привязка к справочнику тегов
    diagnosis: Optional[str] = None
    tools_used: Optional[str] = None
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    solution_text: Optional[str] = Field(None, min_length=10)  # первое решение

class CaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    symptom_text: Optional[str] = None
    symptom_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None
    diagnosis: Optional[str] = None
    tools_used: Optional[str] = None
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    status: Optional[str] = Field(None, pattern="^(draft|published)$")
    change_summary: Optional[str] = Field(None, max_length=500)

class CaseResponse(BaseModel):
    id: int
    user_id: int
    author_name: Optional[str] = None
    title: str
    description: Optional[str]
    symptom_text: Optional[str]
    diagnosis: Optional[str]
    tools_used: Optional[str]
    difficulty: str
    is_verified: bool
    view_count: int
    helpful_count: int
    status: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    symptoms: List[SymptomResponse] = []
    tags: List[TagResponse] = []
    solutions: List[SolutionResponse] = []
    media: List[CaseMediaResponse] = []

    class Config:
        from_attributes = True

class CaseListItem(BaseModel):
    """Краткая версия для списка"""
    id: int
    title: str
    symptom_text: Optional[str]
    difficulty: str
    is_verified: bool
    view_count: int
    helpful_count: int
    created_at: datetime
    author_name: Optional[str] = None
    symptoms: List[SymptomResponse] = []
    tags: List[TagResponse] = []
    solutions_count: int = 0
    status: Optional[str] = None

    class Config:
        from_attributes = True
