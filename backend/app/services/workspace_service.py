import re
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate

HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


class WorkspaceError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _validate_color(color: str) -> str:
    if not HEX_COLOR_PATTERN.match(color):
        raise WorkspaceError("Color must be a valid hex code (e.g. #3B82F6)", status_code=422)
    return color.upper()


def get_owned_workspace(db: Session, user_id: UUID, workspace_id: UUID) -> Workspace:
    workspace = db.scalar(
        select(Workspace).where(Workspace.id == workspace_id, Workspace.user_id == user_id)
    )
    if workspace is None:
        raise WorkspaceError("Workspace not found", status_code=404)
    return workspace


def list_workspaces(db: Session, user_id: UUID) -> list[Workspace]:
    return list(
        db.scalars(
            select(Workspace)
            .where(Workspace.user_id == user_id)
            .order_by(Workspace.created_at.desc())
        )
    )


def create_workspace(db: Session, user_id: UUID, payload: WorkspaceCreate) -> Workspace:
    name = payload.name.strip()
    if not name:
        raise WorkspaceError("Workspace name is required", status_code=422)

    workspace = Workspace(
        user_id=user_id,
        name=name,
        description=payload.description.strip() if payload.description else None,
        color=_validate_color(payload.color),
        icon=payload.icon.strip() or "folder",
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


def update_workspace(
    db: Session,
    user_id: UUID,
    workspace_id: UUID,
    payload: WorkspaceUpdate,
) -> Workspace:
    workspace = get_owned_workspace(db, user_id, workspace_id)

    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            raise WorkspaceError("Workspace name is required", status_code=422)
        workspace.name = name

    if payload.description is not None:
        workspace.description = payload.description.strip() or None

    if payload.color is not None:
        workspace.color = _validate_color(payload.color)

    if payload.icon is not None:
        icon = payload.icon.strip()
        if not icon:
            raise WorkspaceError("Workspace icon is required", status_code=422)
        workspace.icon = icon

    db.commit()
    db.refresh(workspace)
    return workspace


def delete_workspace(db: Session, user_id: UUID, workspace_id: UUID) -> None:
    workspace = get_owned_workspace(db, user_id, workspace_id)
    db.delete(workspace)
    db.commit()
