from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUser
from app.db.session import get_db
from app.schemas.common import MessageResponse
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate
from app.services.workspace_service import (
    WorkspaceError,
    create_workspace,
    delete_workspace,
    get_owned_workspace,
    list_workspaces,
    update_workspace,
)

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


def _handle_workspace_error(error: WorkspaceError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


@router.get("", response_model=list[WorkspaceResponse])
def list_user_workspaces(current_user: CurrentUser, db: DbSession) -> list[WorkspaceResponse]:
    workspaces = list_workspaces(db, current_user.id)
    return [WorkspaceResponse.model_validate(workspace) for workspace in workspaces]


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_user_workspace(
    payload: WorkspaceCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> WorkspaceResponse:
    try:
        workspace = create_workspace(db, current_user.id, payload)
    except WorkspaceError as exc:
        raise _handle_workspace_error(exc) from exc
    return WorkspaceResponse.model_validate(workspace)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_user_workspace(
    workspace_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> WorkspaceResponse:
    try:
        workspace = get_owned_workspace(db, current_user.id, workspace_id)
    except WorkspaceError as exc:
        raise _handle_workspace_error(exc) from exc
    return WorkspaceResponse.model_validate(workspace)


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
def update_user_workspace(
    workspace_id: UUID,
    payload: WorkspaceUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> WorkspaceResponse:
    try:
        workspace = update_workspace(db, current_user.id, workspace_id, payload)
    except WorkspaceError as exc:
        raise _handle_workspace_error(exc) from exc
    return WorkspaceResponse.model_validate(workspace)


@router.delete("/{workspace_id}", response_model=MessageResponse)
def delete_user_workspace(
    workspace_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> MessageResponse:
    try:
        delete_workspace(db, current_user.id, workspace_id)
    except WorkspaceError as exc:
        raise _handle_workspace_error(exc) from exc
    return MessageResponse(message="Workspace deleted successfully")
