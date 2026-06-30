from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workspace import Folder, Workspace
from app.schemas.workspace import FolderCreate, FolderUpdate
from app.services.workspace_service import get_owned_workspace

class FolderError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def get_owned_folder(db: Session, user_id: UUID, folder_id: UUID) -> Folder:
    folder = db.scalar(
        select(Folder)
        .join(Workspace, Workspace.id == Folder.workspace_id)
        .where(Folder.id == folder_id, Workspace.user_id == user_id)
    )
    if folder is None:
        raise FolderError("Folder not found", status_code=404)
    return folder


def list_folders(db: Session, user_id: UUID, workspace_id: UUID) -> list[Folder]:
    # Validate workspace ownership first
    get_owned_workspace(db, user_id, workspace_id)
    
    return list(
        db.scalars(
            select(Folder)
            .where(Folder.workspace_id == workspace_id)
            .order_by(Folder.sort_order.asc(), Folder.name.asc())
        )
    )


def create_folder(db: Session, user_id: UUID, payload: FolderCreate) -> Folder:
    # Validate workspace ownership
    get_owned_workspace(db, user_id, payload.workspace_id)

    name = payload.name.strip()
    if not name:
        raise FolderError("Folder name is required", status_code=422)

    # Prevent duplicate name in the same workspace (and same parent if needed, but for simplicity: same workspace)
    # The requirement says: "Prevent duplicate folder names within the same workspace."
    existing_folder = db.scalar(
        select(Folder).where(Folder.workspace_id == payload.workspace_id, Folder.name == name)
    )
    if existing_folder:
        raise FolderError("Folder with this name already exists in the workspace", status_code=409)

    # Validate parent folder if provided
    if payload.parent_id:
        parent_folder = get_owned_folder(db, user_id, payload.parent_id)
        if parent_folder.workspace_id != payload.workspace_id:
            raise FolderError("Parent folder must belong to the same workspace", status_code=400)

    folder = Folder(
        workspace_id=payload.workspace_id,
        parent_id=payload.parent_id,
        name=name,
        description=payload.description.strip() if payload.description else None,
        sort_order=0, # default
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


def update_folder(db: Session, user_id: UUID, folder_id: UUID, payload: FolderUpdate) -> Folder:
    folder = get_owned_folder(db, user_id, folder_id)

    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            raise FolderError("Folder name is required", status_code=422)
            
        if name != folder.name:
            existing_folder = db.scalar(
                select(Folder).where(
                    Folder.workspace_id == folder.workspace_id,
                    Folder.name == name
                )
            )
            if existing_folder:
                raise FolderError("Folder with this name already exists in the workspace", status_code=409)
        folder.name = name

    if payload.description is not None:
        folder.description = payload.description.strip() or None

    if payload.parent_id is not None:
        # validate parent
        if payload.parent_id == folder.id:
            raise FolderError("Folder cannot be its own parent", status_code=400)
        
        parent_folder = get_owned_folder(db, user_id, payload.parent_id)
        if parent_folder.workspace_id != folder.workspace_id:
            raise FolderError("Parent folder must belong to the same workspace", status_code=400)
        folder.parent_id = payload.parent_id
        
    if payload.sort_order is not None:
        folder.sort_order = payload.sort_order

    db.commit()
    db.refresh(folder)
    return folder


def delete_folder(db: Session, user_id: UUID, folder_id: UUID) -> None:
    folder = get_owned_folder(db, user_id, folder_id)
    db.delete(folder)
    db.commit()
