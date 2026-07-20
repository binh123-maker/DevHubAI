import sys
import time
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.document import DocumentVersion, DocumentStructureNode, DocumentBinary
from app.services.document_structure.document_structure_analyzer import analyze_document_structure

def rebuild_all_structures():
    db = SessionLocal()
    try:
        versions = list(db.scalars(select(DocumentVersion)))
        print(f"Found {len(versions)} document versions to rebuild.")
        
        start_time = time.time()
        for idx, version in enumerate(versions, start=1):
            print(f"[{idx}/{len(versions)}] Rebuilding version {version.id}...")
            
            db.query(DocumentStructureNode).filter(DocumentStructureNode.document_version_id == version.id).delete()
            db.commit()
            
            binary = db.scalar(select(DocumentBinary).where(DocumentBinary.sha256 == version.binary_id))
            if not binary or not binary.file_path:
                print(f"Skipping version {version.id}: no binary path.")
                continue
                
            file_path = Path(binary.file_path)
            if not file_path.exists():
                print(f"Skipping version {version.id}: file does not exist: {file_path}")
                continue
                
            try:
                node_dicts = analyze_document_structure(version.id, file_path, binary.file_type)
                
                nodes = []
                for d in node_dicts:
                    nodes.append(
                        DocumentStructureNode(
                            id=d["id"],
                            document_version_id=d["document_version_id"],
                            node_category=d["node_category"],
                            node_type=d["node_type"],
                            parent_id=d["parent_id"],
                            order_index=d["order_index"],
                            hierarchy_level=d["hierarchy_level"],
                            page_start=d["page_start"],
                            page_end=d["page_end"],
                            char_start=d["char_start"],
                            char_end=d["char_end"],
                            line_start=d["line_start"],
                            line_end=d["line_end"],
                            language=d["language"],
                            content_text=d["content_text"],
                            content_markdown=d["content_markdown"],
                            metadata_json=d["metadata_json"]
                        )
                    )
                db.add_all(nodes)
                db.commit()
                print(f"Successfully rebuilt version {version.id}.")
            except Exception as e:
                db.rollback()
                print(f"Failed to rebuild version {version.id}: {e}")
                
        end_time = time.time()
        duration = end_time - start_time
        print(f"Rebuild completed in {duration:.2f} seconds.")
        return len(versions), duration
    finally:
        db.close()

if __name__ == "__main__":
    rebuild_all_structures()
