from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import router

app = FastAPI(title="PianoTechniciansClub API", version="1.0.0")

# ===== ИСПРАВЛЕННЫЕ CORS НАСТРОЙКИ =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "PianoTechniciansClub API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}