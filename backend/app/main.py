from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import router

app = FastAPI(title="PianoTechniciansClub API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ПОДКЛЮЧАЕМ РОУТЕР С ПРЕФИКСОМ /api/v1
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "PianoTechniciansClub API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}