from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUser
from app.db.session import get_db
from app.schemas.common import MessageResponse
from app.schemas.workspace import FolderCreate, FolderResponse, FolderUpdate
from app.services import folder_service

router = APIRouter()


@router.get("", response_model=list[FolderResponse])
def list_folders(
    workspace_id: UUID, 
    current_user: CurrentUser,
    db: Session = Depends(get_db)
) -> list[FolderResponse]:
    try:
        return folder_service.list_folders(db, current_user.id, workspace_id)
    except folder_service.FolderError as e:
        # Actually workspace ownership might throw WorkspaceError, so let's import it or just catch Exception
        # Better: let's catch standard WorkspaceError too
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        from app.services.workspace_service import WorkspaceError
        if isinstance(e, WorkspaceError):
            raise HTTPException(status_code=e.status_code, detail=e.message)
        raise

@router.post("", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
def create_folder(
    payload: FolderCreate, 
    current_user: CurrentUser,
    db: Session = Depends(get_db)
) -> FolderResponse:
    try:
        return folder_service.create_folder(db, current_user.id, payload)
    except folder_service.FolderError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        from app.services.workspace_service import WorkspaceError
        if isinstance(e, WorkspaceError):
            raise HTTPException(status_code=e.status_code, detail=e.message)
        raise


@router.get("/{folder_id}", response_model=FolderResponse)
def get_folder(
    folder_id: UUID, 
    current_user: CurrentUser,
    db: Session = Depends(get_db)
) -> FolderResponse:
    try:
        return folder_service.get_owned_folder(db, current_user.id, folder_id)
    except folder_service.FolderError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{folder_id}", response_model=FolderResponse)
def update_folder(
    folder_id: UUID, 
    payload: FolderUpdate, 
    current_user: CurrentUser,
    db: Session = Depends(get_db)
) -> FolderResponse:
    try:
        return folder_service.update_folder(db, current_user.id, folder_id, payload)
    except folder_service.FolderError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{folder_id}", response_model=MessageResponse)
def delete_folder(
    folder_id: UUID, 
    current_user: CurrentUser,
    db: Session = Depends(get_db)
) -> MessageResponse:
    try:
        folder_service.delete_folder(db, current_user.id, folder_id)
        return MessageResponse(message="Folder deleted successfully")
    except folder_service.FolderError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
