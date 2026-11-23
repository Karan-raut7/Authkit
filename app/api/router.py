from fastapi import APIRouter, Depends
from app.api.v1.router import router as v1_router
from app.security.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

router.include_router(v1_router, prefix="/v1")


@router.get("/me")
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
    }