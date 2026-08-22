from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import router

app = FastAPI(title="PianoTechniciansClub API", version="1.0.0")

# ===== CORS — ПОЛНОСТЬЮ РАЗРЕШАЕМ =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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