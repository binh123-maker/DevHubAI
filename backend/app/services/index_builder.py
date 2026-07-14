from abc import ABC, abstractmethod
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, update
from app.models.document import DocumentChunk

class BaseIndexBuilder(ABC):
    @abstractmethod
    def index_version_chunks(self, db: Session, version_id: UUID) -> None:
        """Abstract method to build search indexes for a specific version's chunks."""
        pass

class PostgresIndexBuilder(BaseIndexBuilder):
    def index_version_chunks(self, db: Session, version_id: UUID) -> None:
        """Update PostgreSQL Full Text Search vector for the chunks of this document version."""
        db.execute(
            update(DocumentChunk)
            .where(DocumentChunk.document_version_id == version_id)
            .values(search_vector=func.to_tsvector('simple', DocumentChunk.content))
        )
        db.commit()
