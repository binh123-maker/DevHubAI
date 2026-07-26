from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUser
from app.db.session import get_db
from app.schemas.dashboard import UserDashboardOverviewResponse, HeatmapDay
from app.services import dashboard_service

router = APIRouter()


@router.get("/overview", response_model=UserDashboardOverviewResponse)
def get_dashboard_overview(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
) -> UserDashboardOverviewResponse:
    try:
        return dashboard_service.get_dashboard_overview(db, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể tải thông tin dashboard: {str(e)}"
        )


@router.get("/heatmap", response_model=list[HeatmapDay])
def get_dashboard_heatmap(
    current_user: CurrentUser,
    days: int = Query(default=90, ge=7, le=365),
    db: Session = Depends(get_db)
) -> list[HeatmapDay]:
    try:
        overview = dashboard_service.get_dashboard_overview(db, current_user)
        return overview.heatmap[-days:]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể tải thông tin heatmap: {str(e)}"
        )
