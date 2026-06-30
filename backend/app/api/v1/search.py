from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUser
from app.db.session import get_db
from app.schemas.search import SearchResult
from app.services import search_service

router = APIRouter()

DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[SearchResult])
def search(
    current_user: CurrentUser,
    db: DbSession,
    query: str = Query(..., min_length=1),
    workspace_id: Optional[UUID] = Query(None),
    limit: int = Query(10, ge=1, le=100),
) -> list[SearchResult]:
    """Search documents across workspaces or within a specific workspace."""
    return search_service.search_documents(
        db=db,
        user_id=current_user.id,
        query=query,
        workspace_id=workspace_id,
        limit=limit,
    )
