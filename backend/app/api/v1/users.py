from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUser
from app.db.session import get_db
from app.schemas.user import UserProfileResponse, UserProfileUpdate
from app.schemas.profile import UserDashboardResponse, ProfileUpdateRequest
from app.services.auth_service import to_user_response
from app.services import profile_service, chat_service


router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
def get_profile(current_user: CurrentUser) -> UserProfileResponse:
    return to_user_response(current_user)


@router.put("/me", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def update_profile(_: UserProfileUpdate, __: CurrentUser) -> UserProfileResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/me/dashboard", response_model=UserDashboardResponse)
def get_dashboard(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
) -> UserDashboardResponse:
    try:
        return profile_service.get_user_dashboard(db, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard data: {str(e)}"
        )


@router.delete("/me/chats", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_chats(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    try:
        chat_service.delete_all_chats(db, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chats: {str(e)}"
        )


@router.patch("/me/profile", response_model=UserDashboardResponse)
def update_user_profile(
    payload: ProfileUpdateRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
) -> UserDashboardResponse:
    try:
        return profile_service.update_user_profile(db, current_user, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

