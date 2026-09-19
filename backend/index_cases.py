"""Индексирует все существующие кейсы в Qdrant для RAG-поиска"""
import sys
sys.path.insert(0, '/app')

from app.database import SessionLocal
from app.models import Case
from app.services.rag_service import rag_service

db = SessionLocal()
cases = db.query(Case).all()

print(f"📚 Найдено {len(cases)} кейсов для индексации...")

for case in cases:
    try:
        rag_service.index_case(
            case_id=case.id,
            title=case.title,
            symptom=case.symptom,
            solution=case.solution,
            tags=[t.tag for t in case.tags]
        )
        print(f"  ✅ Кейс #{case.id}: {case.title}")
    except Exception as e:
        print(f"  ❌ Кейс #{case.id}: {e}")

print(f"\n🎉 Индексация завершена!")
db.close()
