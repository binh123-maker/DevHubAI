from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUser
from app.schemas.user import UserProfileResponse, UserProfileUpdate
from app.services.auth_service import to_user_response

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
def get_profile(current_user: CurrentUser) -> UserProfileResponse:
    return to_user_response(current_user)


@router.put("/me", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def update_profile(_: UserProfileUpdate, __: CurrentUser) -> UserProfileResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
