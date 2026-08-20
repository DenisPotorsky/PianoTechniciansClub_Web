from fastapi import APIRouter

# Создаём роутер
router = APIRouter()

# Импортируем эндпоинты
from app.api.v1.endpoints import auth, admin, calculator, age, regulating

# Регистрируем роутеры
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(admin.router, prefix="/admin", tags=["admin"])
router.include_router(calculator.router, prefix="/calculator", tags=["calculator"])
router.include_router(age.router, prefix="/age", tags=["age"])
router.include_router(regulating.router, prefix="/regulating", tags=["regulating"])