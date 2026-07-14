import logging
import uuid
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document, DocumentChunk, DocumentStructureNode, UrlResource
from app.models.enums import DocumentStatus
from app.services.folder_service import get_owned_folder
from app.services.workspace_service import get_owned_workspace

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(settings.upload_dir)
MAX_FILE_SIZE = settings.max_upload_size_mb * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
}

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class DocumentError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def validate_file(file: UploadFile) -> None:
    # Check extension
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise DocumentError(
            f"File type not allowed. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}",
            status_code=422,
        )

    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise DocumentError(
            f"File type not allowed. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}",
            status_code=422,
        )


def get_owned_document(db: Session, user_id: UUID, document_id: UUID) -> Document:
    document = db.scalar(
        select(Document).where(Document.id == document_id, Document.user_id == user_id)
    )
    if not document:
        raise DocumentError("Document not found", status_code=404)
    return document


def list_documents(db: Session, user_id: UUID, workspace_id: UUID, folder_id: UUID | None = None) -> list[Document]:
    # Validate workspace ownership
    get_owned_workspace(db, user_id, workspace_id)
    
    query = select(Document).where(Document.workspace_id == workspace_id)
    if folder_id:
        query = query.where(Document.folder_id == folder_id)
    else:
        query = query.where(Document.folder_id.is_(None))
        
    return list(db.scalars(query.order_by(Document.created_at.desc())))


def calculate_sha256(file_path: Path) -> str:
    import hashlib
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def upload_document(
    db: Session,
    user_id: UUID,
    workspace_id: UUID,
    folder_id: UUID | None,
    file: UploadFile,
    title: str | None,
    description: str | None,
) -> Document:
    # 1. Validate ownership
    get_owned_workspace(db, user_id, workspace_id)
    if folder_id:
        folder = get_owned_folder(db, user_id, folder_id)
        if folder.workspace_id != workspace_id:
            raise DocumentError("Folder does not belong to the specified workspace", status_code=400)

    # 2. Validate file type
    validate_file(file)

    # 3. Create unique file path for temporary saving
    file_id = uuid.uuid4()
    ext = Path(file.filename or "").suffix.lower()
    temp_filename = f"temp_{file_id}{ext}"
    workspace_dir = UPLOAD_DIR / str(workspace_id)
    workspace_dir.mkdir(parents=True, exist_ok=True)
    temp_file_path = workspace_dir / temp_filename

    # 4. Save file and get size
    file_size = 0
    try:
        with open(temp_file_path, "wb") as buffer:
            while chunk := file.file.read(8192):
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    raise DocumentError(f"File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024):.0f}MB", status_code=413)
                buffer.write(chunk)

        # Compute SHA-256
        sha256 = calculate_sha256(temp_file_path)

        # 5. Check duplicate DocumentBinary (CAS)
        from app.models.document import DocumentBinary, DocumentVersion, ProcessingJob
        binary = db.scalar(select(DocumentBinary).where(DocumentBinary.sha256 == sha256))
        if binary:
            # Duplicate binary found, delete temp file and reuse path
            temp_file_path.unlink(missing_ok=True)
        else:
            # Unique content, rename temp file to permanent CAS path
            cas_filename = f"{sha256}{ext}"
            final_file_path = workspace_dir / cas_filename
            temp_file_path.rename(final_file_path)
            binary = DocumentBinary(
                sha256=sha256,
                file_path=str(final_file_path),
                file_type=ext.lstrip("."),
                file_size=file_size,
            )
            db.add(binary)
            db.commit()

        # 6. Save logical Document
        doc_title = title.strip() if title else (file.filename or "Untitled")
        document = Document(
            id=file_id,
            user_id=user_id,
            workspace_id=workspace_id,
            folder_id=folder_id,
            title=doc_title,
            description=description.strip() if description else None,
            file_name=file.filename or "unknown",
            file_type=ext.lstrip("."),
            file_size=file_size,
            file_path=binary.file_path,
            status=DocumentStatus.UPLOADING,
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        # 7. Save DocumentVersion
        version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            binary_id=binary.sha256,
            status=DocumentStatus.UPLOADING,
        )
        db.add(version)
        db.commit()
        db.refresh(version)

        # 8. Save ProcessingJob
        job = ProcessingJob(
            document_version_id=version.id,
            job_type="upload_processing",
            status="pending",
            priority=1,
            progress=0,
        )
        db.add(job)
        db.commit()

        return document
    except Exception as e:
        if temp_file_path.exists():
            temp_file_path.unlink(missing_ok=True)
        raise e


def trigger_job_processing(job_id: UUID) -> None:
    """Run the processing job synchronously (called from BackgroundTask)."""
    from app.db.session import SessionLocal
    from app.services.processing_service import execute_processing_job

    # Reuse testing session if running in a test client environment to see uncommitted data
    from app.main import app
    from app.db.session import get_db
    if app.dependency_overrides.get(get_db):
        db = next(app.dependency_overrides[get_db]())
    else:
        db = SessionLocal()
    try:
        execute_processing_job(db, job_id)
    except Exception as exc:
        logger.exception("Failed to execute processing job %s: %s", job_id, exc)
    finally:
        db.close()


def trigger_processing_task(document_id: UUID) -> None:
    """Run the document processing pipeline synchronously (called from BackgroundTask)."""
    from app.db.session import SessionLocal
    from app.models.document import DocumentVersion, ProcessingJob

    # Reuse testing session if running in a test client environment to see uncommitted data
    from app.main import app
    from app.db.session import get_db
    if app.dependency_overrides.get(get_db):
        db = next(app.dependency_overrides[get_db]())
    else:
        db = SessionLocal()
    try:
        # Find the latest pending job for this document
        version = db.scalar(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
        )
        if version:
            job = db.scalar(
                select(ProcessingJob)
                .where(ProcessingJob.document_version_id == version.id, ProcessingJob.status == "pending")
            )
            if job:
                trigger_job_processing(job.id)
                return

        # Fallback to legacy processing if no version exists
        from app.services.processing_service import process_document
        document = db.scalar(select(Document).where(Document.id == document_id))
        if document:
            process_document(db, document)
    except Exception as exc:
        logger.exception("Failed to process document %s: %s", document_id, exc)
        db.rollback()
        document = db.scalar(select(Document).where(Document.id == document_id))
        if document:
            document.status = DocumentStatus.FAILED
            db.commit()
    finally:
        db.close()



def get_document_chunks(db: Session, user_id: UUID, document_id: UUID) -> list[DocumentChunk]:
    """Return all chunks for a document the user owns, ordered by chunk_index."""
    document = get_owned_document(db, user_id, document_id)
    return (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document.id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )


def delete_document(db: Session, user_id: UUID, document_id: UUID) -> None:
    document = get_owned_document(db, user_id, document_id)
    
    # Delete physical file
    if document.file_path:
        file_path = Path(document.file_path)
        if file_path.is_file():
            file_path.unlink(missing_ok=True)
        
    db.delete(document)
    db.commit()


def update_document(
    db: Session,
    user_id: UUID,
    document_id: UUID,
    title: str,
    description: str | None,
) -> Document:
    """Rename (and optionally redescribe) a document the user owns."""
    document = get_owned_document(db, user_id, document_id)

    title = title.strip()
    if not title:
        raise DocumentError("Title cannot be empty", status_code=422)
    if len(title) > 255:
        raise DocumentError("Title must be 255 characters or fewer", status_code=422)

    document.title = title
    document.description = description.strip() if description else None

    db.commit()
    db.refresh(document)
    return document


def bulk_delete_documents(db: Session, user_id: UUID, document_ids: list[UUID]) -> int:
    """Delete multiple documents owned by user_id. Returns the count of deleted documents."""
    count = 0
    for document_id in document_ids:
        try:
            delete_document(db, user_id, document_id)
            count += 1
        except DocumentError:
            continue
        
    return count

def is_safe_url(url: str) -> bool:
    import socket
    import ipaddress
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
        
    hostname = parsed.hostname
    if not hostname:
        return False
        
    if hostname.lower() == "localhost":
        return False
        
    try:
        ips = socket.gethostbyname_ex(hostname)[2]
        for ip in ips:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_unspecified:
                return False
    except socket.gaierror:
        return False
        
    return True

def upload_document_from_url(
    db: Session,
    user_id: UUID,
    workspace_id: UUID,
    folder_id: UUID | None,
    url: str,
    title: str | None,
    description: str | None,
) -> Document:

    if not is_safe_url(url):
        raise DocumentError(
            "Invalid or unsafe URL",
            status_code=400,
        )

    # 1. Validate ownership
    get_owned_workspace(db, user_id, workspace_id)
    if folder_id:
        folder = get_owned_folder(db, user_id, folder_id)
        if folder.workspace_id != workspace_id:
            raise DocumentError("Folder does not belong to the specified workspace", status_code=400)

    # 2. Create placeholder document
    file_id = uuid.uuid4()
    doc_title = title.strip() if title else url
    
    document = Document(
        id=file_id,
        user_id=user_id,
        workspace_id=workspace_id,
        folder_id=folder_id,
        title=doc_title,
        description=description.strip() if description else None,
        file_name="url_download",
        file_type="",
        file_size=0,
        file_path="",
        status=DocumentStatus.UPLOADING,
        source_url=url,
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def extract_metadata(soup, fallback_url: str) -> tuple[str, str]:
    title = fallback_url
    
    # Fix #4: use attrs={} dict for robust parser-independent attribute lookup
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    if og_title and og_title.get('content'):
        title = og_title['content']
    elif soup.title and soup.title.string:
        title = soup.title.string
    else:
        h1 = soup.find('h1')
        if h1 and h1.get_text(strip=True):
            title = h1.get_text(strip=True)
            
    desc = ""
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        desc = meta_desc['content']
    else:
        # Fix #4: use attrs={} dict for og:description too
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            desc = og_desc['content']

    # Fix #2: cap title to 255 chars to match DB VARCHAR column limit
    title = title.strip()[:255]
    return title, desc.strip()


def remove_noise(soup) -> None:
    import re
    useless_tags = ["header", "footer", "nav", "aside", "script", "style", "svg", "canvas", "iframe", "noscript", "form"]
    for tag in soup(useless_tags):
        tag.decompose()
        
    for img in soup("img"):
        img.decompose()
        
    noise_keywords = [
        "sidebar", "menu", "navbar", "navigation", "footer", "header", "toc", 
        "table-of-contents", "breadcrumb", "comments", "comment", "reply", 
        "share", "social", "related", "recommend", "ads", "advertisement", 
        "promo", "banner", "cookie", "newsletter", "pagination", "sponsor", 
        "sponsors", "github-corner",
        "build status", "coverage", "github stars", "pypi", "docker badge", "shields.io"
    ]
    # Fix #5: keep ci as a separate whole-word pattern to avoid matching
    # legitimate substrings like "article", "social", "scientific", etc.
    noise_regex = re.compile(
        r'(?:' + '|'.join(re.escape(k) for k in noise_keywords) + r'|\bci\b)',
        re.IGNORECASE
    )
    
    def is_noisy(tag):
        classes = tag.get('class', [])
        classes_str = ' '.join(classes) if isinstance(classes, list) else str(classes)
        if noise_regex.search(classes_str): return True
        
        tag_id = str(tag.get('id', ''))
        if noise_regex.search(tag_id): return True
        
        alt = str(tag.get('alt', ''))
        if noise_regex.search(alt): return True
        
        return False
        
    for tag in soup.find_all(is_noisy):
        tag.decompose()
        
    # Fix #3: iterate over a reversed list so decomposing a parent does not
    # corrupt the traversal of its already-visited children.
    for tag in reversed(soup.find_all()):
        if tag.name not in ['br', 'hr']:
            if not tag.contents and not tag.get_text(strip=True):
                tag.decompose()


def extract_main_content(soup):
    article = soup.find('article')
    if article: return article
    main = soup.find('main')
    if main: return main
    role_main = soup.find(attrs={"role": "main"})
    if role_main: return role_main
    body = soup.find('body')
    if body: return body
    return soup


def html_to_markdown(html_content: str) -> str:
    import markdownify
    md = markdownify.markdownify(
        html_content, 
        heading_style="ATX",
        strip=['img'],
        default_title=True
    )
    return md


def normalize_markdown(md_text: str) -> str:
    import re
    md_text = re.sub(r'\n{4,}', '\n\n\n', md_text)
    return md_text.strip()


def clean_html(html_text: str, fallback_url: str) -> tuple[str, str, str]:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_text, 'lxml')
    
    title, desc = extract_metadata(soup, fallback_url)
    remove_noise(soup)
    main_content = extract_main_content(soup)
    
    md_text = html_to_markdown(str(main_content))
    md_text = normalize_markdown(md_text)
    
    return md_text, title, desc


def download_and_process_url(document_id: UUID, url: str) -> None:
    """Download a file from a URL and trigger processing."""
    import httpx
    from urllib.parse import urlparse
    from email.message import EmailMessage
    from app.db.session import SessionLocal
    from app.models.document import DocumentBinary, DocumentVersion, ProcessingJob

    # Reuse testing session if running in a test client environment to see uncommitted data
    from app.main import app
    from app.db.session import get_db
    if app.dependency_overrides.get(get_db):
        db = next(app.dependency_overrides[get_db]())
    else:
        db = SessionLocal()
    temp_file_path = None
    try:
        # Fetch document
        document = db.scalar(select(Document).where(Document.id == document_id))
        if not document:
            return

        with httpx.Client(follow_redirects=True, timeout=120.0) as client:
            with client.stream("GET", url) as response:
                response.raise_for_status()

                ct = response.headers.get("content-type", "")

                filename: str = "url_download"
                ext: str = ""
                size: int = 0
                
                url_resource_id = None
                if "text/html" in ct.lower():
                    response.read()
                    html_content = response.text
                    
                    md_text, page_title, page_desc = clean_html(html_content, url)
                    
                    content_bytes = md_text.encode('utf-8')
                    size = len(content_bytes)
                    
                    if size > MAX_FILE_SIZE:
                        raise ValueError(f"File too large. Max size is {MAX_FILE_SIZE / (1024 * 1024):.0f}MB")
                        
                    filename = f"webpage.md"
                    safe_title = "".join([c for c in page_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                    if safe_title:
                        filename = f"{safe_title[:50]}.md"
                    ext = ".md"
                    
                    workspace_dir = UPLOAD_DIR / str(document.workspace_id)
                    workspace_dir.mkdir(parents=True, exist_ok=True)
                    temp_file_path = workspace_dir / f"temp_url_{document.id}{ext}"
                    
                    with open(temp_file_path, "wb") as f:
                        f.write(content_bytes)
                        
                    if page_title and (document.title == url or not document.title):
                        document.title = page_title
                    if page_desc and not document.description:
                        document.description = page_desc
                        
                    # Save UrlResource
                    from app.models.document import UrlResource
                    url_res = db.scalar(select(UrlResource).where(UrlResource.original_url == url))
                    if not url_res:
                        url_res = UrlResource(
                            original_url=url,
                            fetched_html=html_content,
                            parsed_markdown=md_text,
                            title=page_title,
                            description=page_desc,
                        )
                        db.add(url_res)
                        db.commit()
                        db.refresh(url_res)
                    url_resource_id = url_res.id
                        
                else:
                    # Determine filename
                    filename = "downloaded"
                    cd = response.headers.get("content-disposition")
                    if cd:
                        msg = EmailMessage()
                        msg['content-disposition'] = cd
                        parsed_filename = msg.get_filename()
                        if parsed_filename:
                            filename = parsed_filename
                    else:
                        path = urlparse(url).path
                        if path:
                            name = Path(path).name
                            if name:
                                filename = name
                    
                    ext = Path(filename).suffix.lower()
                    if not ext:
                        if "pdf" in ct: ext = ".pdf"
                        elif "markdown" in ct: ext = ".md"
                        elif "plain" in ct: ext = ".txt"
                        elif "wordprocessingml" in ct: ext = ".docx"
                    
                    if ext not in ALLOWED_EXTENSIONS:
                        raise ValueError(f"Unsupported file extension: {ext}")
                    
                    # Setup path
                    workspace_dir = UPLOAD_DIR / str(document.workspace_id)
                    workspace_dir.mkdir(parents=True, exist_ok=True)
                    temp_file_path = workspace_dir / f"temp_url_{document.id}{ext}"

                    size = 0
                    with open(temp_file_path, "wb") as f:
                        for chunk in response.iter_bytes(chunk_size=8192):
                            size += len(chunk)
                            if size > MAX_FILE_SIZE:
                                raise ValueError(f"File too large. Max size is {MAX_FILE_SIZE / (1024 * 1024):.0f}MB")
                            f.write(chunk)

        # Compute SHA-256
        sha256 = calculate_sha256(temp_file_path)

        # Check duplicate DocumentBinary (CAS)
        binary = db.scalar(select(DocumentBinary).where(DocumentBinary.sha256 == sha256))
        if binary:
            # Duplicate binary found, delete temp file and reuse path
            temp_file_path.unlink(missing_ok=True)
        else:
            # Unique content, rename temp file to permanent CAS path
            cas_filename = f"{sha256}{ext}"
            final_file_path = workspace_dir / cas_filename
            temp_file_path.rename(final_file_path)
            binary = DocumentBinary(
                sha256=sha256,
                file_path=str(final_file_path),
                file_type=ext.lstrip("."),
                file_size=size,
            )
            db.add(binary)
            db.commit()

        # Update document columns
        document.file_name = filename
        document.file_type = ext.lstrip(".")
        document.file_size = size
        document.file_path = binary.file_path
        document.status = DocumentStatus.UPLOADING
        db.commit()

        # Create DocumentVersion
        version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            binary_id=binary.sha256,
            url_resource_id=url_resource_id,
            status=DocumentStatus.UPLOADING,
        )
        db.add(version)
        db.commit()
        db.refresh(version)

        # Create ProcessingJob
        job = ProcessingJob(
            document_version_id=version.id,
            job_type="url_processing",
            status="pending",
            priority=1,
            progress=0,
        )
        db.add(job)
        db.commit()

        # Trigger processing job
        trigger_job_processing(job.id)

    except Exception as exc:
        logger.exception("Failed to download URL %s for document %s: %s", url, document_id, exc)
        db.rollback()
        
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink(missing_ok=True)
            
        doc = db.scalar(select(Document).where(Document.id == document_id))
        if doc:
            doc.status = DocumentStatus.FAILED
            doc.file_name = "url_download"
            doc.file_type = ""
            doc.file_size = 0
            doc.file_path = ""
            db.commit()
    finally:
        db.close()


def get_document_structure(db: Session, user_id: UUID, document_id: UUID) -> list[DocumentStructureNode]:
    # 1. Verify ownership
    document = get_owned_document(db, user_id, document_id)
    
    # 2. Find latest version
    from app.models.document import DocumentVersion, DocumentStructureNode
    version = db.scalar(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == document.id)
        .order_by(DocumentVersion.version_number.desc())
    )
    if not version:
        return []
        
    # 3. Retrieve structure nodes
    query = (
        select(DocumentStructureNode)
        .where(DocumentStructureNode.document_version_id == version.id)
        .order_by(DocumentStructureNode.order_index.asc())
    )
    return list(db.scalars(query))


def get_url_resource(db: Session, user_id: UUID, document_id: UUID) -> UrlResource | None:
    # 1. Verify ownership
    document = get_owned_document(db, user_id, document_id)
    
    # 2. Find latest version
    from app.models.document import DocumentVersion, UrlResource
    version = db.scalar(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == document.id)
        .order_by(DocumentVersion.version_number.desc())
    )
    if not version or not version.url_resource_id:
        return None
        
    return db.scalar(select(UrlResource).where(UrlResource.id == version.url_resource_id))



