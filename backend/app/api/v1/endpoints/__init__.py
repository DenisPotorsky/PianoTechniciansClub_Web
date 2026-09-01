from fastapi import APIRouter
from app.api.v1.endpoints import auth, admin, calculator, age, regulating, strings, users

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(admin.router, prefix="/admin", tags=["admin"])
router.include_router(calculator.router, prefix="/calculator", tags=["calculator"])
router.include_router(age.router, prefix="/age", tags=["age"])
router.include_router(regulating.router, prefix="/regulating", tags=["regulating"])
router.include_router(strings.router, prefix="/strings", tags=["strings"])
router.include_router(users.router, prefix="/users", tags=["users"])