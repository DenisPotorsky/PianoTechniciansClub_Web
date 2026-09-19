from fastapi import APIRouter, Query
from typing import List
from app.services.rag_service import rag_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/search")
def ai_search(q: str = Query(..., min_length=3, description="Поисковый запрос")):
    """AI-поиск по базе знаний с использованием RAG"""
    results = rag_service.search(q, limit=5)
    return {"query": q, "results": results}
